# ~/sdn_ddos_project/ryu_controller/ddos_web_app.py

import json
import time
from datetime import datetime
from functools import wraps
from ryu.app.wsgi import ControllerBase, WSGIApplication, route, Response
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet
from ryu.lib import hub
from ryu.topology.api import get_all_switch, get_all_link, get_all_host

# --- CORS 装饰器 ---
def cors_enabled(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        response = f(*args, **kwargs)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    return wrapper

# --- Web API 控制器 ---
class DDoSWebController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(DDoSWebController, self).__init__(req, link, data, **config)
        self.ddos_app = data['ddos_app_instance']

    # --- 核心API ---
    @route('api', '/api/alerts', methods=['GET'])
    @cors_enabled
    def get_ddos_alerts(self, req, **kwargs):
        body = json.dumps({
            'blacklist': list(self.ddos_app.blacklist),
            'alerts': self.ddos_app.alerts
        })
        return Response(content_type='application/json', body=body)

    @route('api', '/api/traffic-stats', methods=['GET'])
    @cors_enabled
    def get_traffic_stats(self, req, **kwargs):
        body = json.dumps(self.ddos_app.traffic_history)
        return Response(content_type='application/json', body=body)

    # --- 拓扑API ---
    @route('api', '/api/topology/switches', methods=['GET'])
    @cors_enabled
    def get_switches_api(self, req, **kwargs):
        switches = get_all_switch(self.ddos_app)
        body = json.dumps([switch.to_dict() for switch in switches])
        return Response(content_type='application/json', body=body)

    @route('api', '/api/topology/links', methods=['GET'])
    @cors_enabled
    def get_links_api(self, req, **kwargs):
        links = get_all_link(self.ddos_app)
        body = json.dumps([link.to_dict() for link in links])
        return Response(content_type='application/json', body=body)

    @route('api', '/api/topology/hosts', methods=['GET'])
    @cors_enabled
    def get_hosts_api(self, req, **kwargs):
        hosts = get_all_host(self.ddos_app)
        body = json.dumps([host.to_dict() for host in hosts])
        return Response(content_type='application/json', body=body)
        
    # --- 黑白名单管理 API ---
    @route('api', '/api/lists', methods=['GET'])
    @cors_enabled
    def get_lists(self, req, **kwargs):
        body = json.dumps({
            'blacklist': list(self.ddos_app.blacklist),
            'whitelist': list(self.ddos_app.whitelist)
        })
        return Response(content_type='application/json', body=body)

    @route('api', '/api/lists/add', methods=['POST', 'OPTIONS'])
    @cors_enabled
    def add_to_list(self, req, **kwargs):
        if req.method == 'OPTIONS':
            return Response(status=200)
        try:
            data = req.json_body
            list_type = data.get('type')
            mac = data.get('mac')
            result = self.ddos_app.add_to_list(list_type, mac)
            return Response(status=200, body=json.dumps(result))
        except Exception as e:
            return Response(status=500, body=json.dumps({'error': str(e)}))

    @route('api', '/api/lists/remove', methods=['POST', 'OPTIONS'])
    @cors_enabled
    def remove_from_list(self, req, **kwargs):
        if req.method == 'OPTIONS':
            return Response(status=200)
        try:
            data = req.json_body
            list_type = data.get('type')
            mac = data.get('mac')
            result = self.ddos_app.remove_from_list(list_type, mac)
            return Response(status=200, body=json.dumps(result))
        except Exception as e:
            return Response(status=500, body=json.dumps({'error': str(e)}))

# --- SDN 应用核心逻辑 ---
class DDoSApp(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {'wsgi': WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(DDoSApp, self).__init__(*args, **kwargs)
        # 基础数据结构
        self.mac_to_port = {}
        self.datapaths = {}
        
        # DDoS 检测与名单管理
        self.blacklist = set()
        self.whitelist = set()
        self.alerts = {}
        self.ddos_threshold = 100 # PPS
        
        # 流量统计
        self.flow_stats = {}
        self.sleep_time = 5
        self.traffic_history = []
        self.previous_total_packets = {}

        # 启动后台监控协程
        self.monitor_thread = hub.spawn(self._monitor)
        
        # 注册 Web API 控制器
        wsgi = kwargs['wsgi']
        wsgi.register(DDoSWebController, {'ddos_app_instance': self})
        self.logger.info("DDoS Web App Initialized.")

    # --- 黑白名单管理逻辑 ---
    def add_to_list(self, list_type, mac):
        if list_type == 'blacklist':
            if mac not in self.blacklist:
                self.blacklist.add(mac)
                self.logger.info(f"Manually added {mac} to blacklist.")
                self._block_mac(mac)
                return {'status': 'success', 'message': f'{mac} added to blacklist.'}
        elif list_type == 'whitelist':
            if mac not in self.whitelist:
                self.whitelist.add(mac)
                self.logger.info(f"Manually added {mac} to whitelist.")
                # 如果在黑名单中，则移除
                if mac in self.blacklist:
                    self.remove_from_list('blacklist', mac)
                return {'status': 'success', 'message': f'{mac} added to whitelist.'}
        return {'status': 'error', 'message': 'Invalid list type or MAC already exists.'}

    def remove_from_list(self, list_type, mac):
        if list_type == 'blacklist':
            if mac in self.blacklist:
                self.blacklist.remove(mac)
                if mac in self.alerts:
                    del self.alerts[mac]
                self.logger.info(f"Manually removed {mac} from blacklist.")
                self._unblock_mac(mac)
                return {'status': 'success', 'message': f'{mac} removed from blacklist.'}
        elif list_type == 'whitelist':
            if mac in self.whitelist:
                self.whitelist.remove(mac)
                self.logger.info(f"Manually removed {mac} from whitelist.")
                return {'status': 'success', 'message': f'{mac} removed from whitelist.'}
        return {'status': 'error', 'message': 'MAC not found in the specified list.'}
        
    def _block_mac(self, mac):
        for datapath in self.datapaths.values():
            parser = datapath.ofproto_parser
            match = parser.OFPMatch(eth_src=mac)
            self.add_flow(datapath, 2, match, []) # 优先级2，空action=丢弃
            
    def _unblock_mac(self, mac):
        for datapath in self.datapaths.values():
            parser = datapath.ofproto_parser
            match = parser.OFPMatch(eth_src=mac)
            mod = parser.OFPFlowMod(
                datapath=datapath,
                command=datapath.ofproto.OFPFC_DELETE,
                out_port=datapath.ofproto.OFPP_ANY,
                out_group=datapath.ofproto.OFPG_ANY,
                priority=2,
                match=match)
            datapath.send_msg(mod)
            
    # --- 后台监控与统计 ---
    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(self.sleep_time)

    def _request_stats(self, datapath):
    
        # 下面所有行都向右缩进了4个空格
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # 关键修正：使用最标准的方式请求所有流表的统计
        req = parser.OFPFlowStatsRequest(datapath, 0,
                                         ofproto.OFPTT_ALL,  # 请求所有流表 (table_id)
                                         ofproto.OFPP_ANY,   # 不限出端口
                                         ofproto.OFPG_ANY,   # 不限组
                                         0, 0,               # cookie and cookie_mask
                                         parser.OFPMatch())   # 空的match，匹配所有流
        datapath.send_msg(req)
        
        
    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body
        dpid = ev.msg.datapath.id

        # 告警检测
        self.flow_stats.setdefault(dpid, {})
        for stat in body:
            if 'eth_src' in stat.match and stat.match['eth_src'] not in self.whitelist:
                flow_key = (dpid, stat.match['eth_src'])
                if flow_key in self.flow_stats[dpid]:
                    last_stats = self.flow_stats[dpid][flow_key]
                    pps = (stat.packet_count - last_stats['packet_count']) / self.sleep_time
                    if pps > self.ddos_threshold:
                        attacker_src = stat.match['eth_src']
                        self.alerts[attacker_src] = {'pps': round(pps, 2), 'dpid': dpid}
                        if attacker_src not in self.blacklist:
                            self.blacklist.add(attacker_src)
                            self.logger.warning(f"[DDoS DETECTED] {attacker_src} added to blacklist (PPS: {pps:.2f}).")
                            self._block_mac(attacker_src)
                self.flow_stats[dpid][flow_key] = {'packet_count': stat.packet_count}

        # 总流量统计
        current_total_packets = sum([s.packet_count for s in body])
        last_total_packets = self.previous_total_packets.get(dpid, 0)
        
        if last_total_packets > 0:
            total_pps = (current_total_packets - last_total_packets) / self.sleep_time
            if dpid == 1: # 只记录s1的流量作为代表
                timestamp_str = datetime.now().strftime("%H:%M:%S")
                self.traffic_history.append({'time': timestamp_str, 'pps': round(total_pps, 2)})
                if len(self.traffic_history) > 12: self.traffic_history.pop(0)

        self.previous_total_packets[dpid] = current_total_packets
    
    # --- OpenFlow 事件处理 ---
    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths: del self.datapaths[datapath.id]
            if datapath.id in self.previous_total_packets: del self.previous_total_packets[datapath.id]

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        ofproto, parser = datapath.ofproto, datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg, datapath = ev.msg, ev.msg.datapath
        ofproto, parser = datapath.ofproto, datapath.ofproto_parser
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        src, dst, dpid = eth.src, eth.dst, datapath.id

        if src in self.blacklist or src in self.whitelist:
            if src in self.blacklist: return # 黑名单直接丢弃

        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port

        out_port = self.mac_to_port[dpid].get(dst, ofproto.OFPP_FLOOD)
        actions = [parser.OFPActionOutput(out_port)]

        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            self.add_flow(datapath, 1, match, actions)

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=msg.data)
        datapath.send_msg(out)
        
        
        print(qqq)
