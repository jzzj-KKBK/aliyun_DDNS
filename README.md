# 智能DNS负载均衡控制器

## 概述
本脚本实现基于实时网络状况的智能DNS负载均衡，主要功能包括：
- 动态监控Gost代理服务器状态
- 多节点延迟检测与连接数统计
- 阿里云DNS记录自动更新
- 负载均衡策略自动切换



协同内网穿透，完成流量的负载均衡，同时平衡玩家延迟，降低单个节点的流量需求。这样就可以用廉价的部署来完成高流量的分配，同时在遭受DDOS攻击的时候，能有效防止服务器崩溃，DDOS攻击者只能让单个节点崩溃。

