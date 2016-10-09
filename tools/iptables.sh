#/bin/bash
/sbin/iptables -A INPUT -i lo -j ACCEPT
/sbin/iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
/sbin/iptables -A INPUT -s 0.0.0.0/0.0.0.0 -p tcp --dport 22 -j ACCEPT
/sbin/iptables -A INPUT -s 0.0.0.0/0.0.0.0 -p tcp --dport 80 -j ACCEPT
/sbin/iptables -A INPUT -s 0.0.0.0/0.0.0.0 -p tcp --dport 443 -j ACCEPT
/sbin/iptables -A INPUT -s 0.0.0.0/0.0.0.0 -p tcp --dport 7248 -j ACCEPT
/sbin/iptables -A INPUT -p icmp -j ACCEPT
/sbin/iptables -P INPUT DROP


iptables -A INPUT -p udp --dport 1701 -j ACCEPT
 678  iptables -A INPUT -p udp --dport 500 -j ACCEPT
 679  iptables -A INPUT -p udp --dport 4500 -j ACCEPT
 684  iptables -L-n
 685  iptables -L -n
 686  iptables -A INPUT -p tcp --dport 1701 -j ACCEPT
 687  iptables -A INPUT -p tcp --dport 500 -j ACCEPT
 688  iptables -A INPUT -p tcp --dport 4500 -j ACCEPT

iptables -A INPUT -p tcp -m state --state NEW --dport 80 -j ACCEPT
iptables -A INPUT -p udp -m state --state NEW --dport 80 -j ACCEPT
iptables -A INPUT -p tcp -m state --state NEW --dport 443 -j ACCEPT
iptables -A INPUT -p udp -m state --state NEW --dport 443 -j ACCEPT
iptables -A INPUT -p tcp -m state --state NEW --dport 22 -j ACCEPT
iptables -A INPUT -p udp -m state --state NEW --dport 22 -j ACCEPT
iptables -A INPUT -p tcp -m state --state NEW --dport 7248 -j ACCEPT
iptables -A INPUT -p udp -m state --state NEW --dport 7248 -j ACCEPT
