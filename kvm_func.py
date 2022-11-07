# -*- coding: utf-8 -*-
import unix
import kvm
import collections
import re
from concurrent.futures import ThreadPoolExecutor

def inspector(LISTOFNODES: list):
    all_res = {}
    execs = []
    with ThreadPoolExecutor(max_workers=len(LISTOFNODES)) as executor:
        for kvm_node in LISTOFNODES:
            execs.append(executor.submit(_inspector, kvm_node))
    for exec_el in execs:
        all_res={**all_res, **dict(exec_el.result())}
    return all_res

def _inspector(kvm_node: str):
    try:
        with unix.connect(kvm_node) as host:
            host_kvm = kvm.Hypervisor(host)
            DOMSTATUS = host_kvm.list_domains(all=True)
            DOMAINS_CPU_USED = []
            DOMAINS_MEMORY_USED = []
            DOMAININFO = []
            DOMAINDISKS = []
            
            for dom_i in DOMSTATUS.items():
                domain_cpu_used = 0
                domain_memory_used = 0
                DOM_COL = collections.UserDict(host_kvm.domain.conf(dom_i[0]))
                dom_disks = [ d['source']['@file'] for d in DOM_COL['devices']['disk'] if d['@device'] == 'disk'] 
                dom_info = {
                        'name': dom_i[0],
                        'state': dom_i[1]['state'],
                        'vcpus': DOM_COL['vcpu']['#text'],
                        'memory': DOM_COL['memory']['#text'],
                        'disks': dom_disks
                        }

                if dom_i[1]['state'] == 'running':
                    domain_cpu_used = DOM_COL['vcpu']['#text']
                    domain_memory_used = DOM_COL['memory']['#text']
                DOMAINS_CPU_USED.append(int(domain_cpu_used))
                DOMAINS_MEMORY_USED.append(int(domain_memory_used))
                DOMAININFO.append(dom_info)
                DOMAINDISKS.extend(dom_disks)
                                
            CMDLINE = 'cat /proc/cpuinfo | grep "model name" | uniq | cut -f2 -d ":"; echo "---"; df -lh | grep -Pv "(udev|tmpfs)" | awk \'{print $1 "*" $2 "*" $4 "*" $6}\' | tail -n+2;echo "---";ip a | grep "vnet" | wc -l;echo "---";hostname;echo "---";du -s'
            pos = 0
            overlen = False
            for disk_path in DOMAINDISKS:
                if (len(CMDLINE) + len(disk_path)) >= 4095:
                    overlen = True
                    break
                else:
                    CMDLINE = f'{CMDLINE} {disk_path}'
                    pos += 1
            host_exec = host.execute(CMDLINE)[1]
            NODEEXECINFO = host_exec.split('---')
            NODEDISKS = [ {"device_name":disk_i.split("*")[0], "device_size":disk_i.split("*")[1], "device_free_size":disk_i.split("*")[2], "mount_point":disk_i.split("*")[3]} for disk_i in NODEEXECINFO[1].split("\n")[1:-1] ]
            VNETCOUNT = int(NODEEXECINFO[2][1:-1])
            HOSTNAME = NODEEXECINFO[3][1:-1]
            DOMAINDISKSSIZE = { disk_i.split("\t")[1]: int(disk_i.split("\t")[0]) for disk_i in NODEEXECINFO[4].split("\n")[1:-1] }
            NODEINFO = host_kvm.hypervisor.nodeinfo()
            if overlen:
                CMDLINE = 'du -s'
                for disk_path in DOMAINDISKS[pos-1:]:
                    CMDLINE = f'{CMDLINE} {disk_path}'
                host_exec = host.execute(CMDLINE)[1]
                DOMAINDISKSSIZE = {**DOMAINDISKSSIZE, **{ disk_i.split("\t")[1]: int(disk_i.split("\t")[0]) for disk_i in host_exec.split("\n")[1:-1] } }
                
            for dom in DOMAININFO:
                dom['disks_sum'] = 0
                dom_disks = {}
                for i in dom['disks']:
                    dom_disks[i] = DOMAINDISKSSIZE[i] if i in DOMAINDISKSSIZE else 0
                    dom['disks_sum'] += DOMAINDISKSSIZE[i] if i in DOMAINDISKSSIZE else 0
                    dom['disks'] = dom_disks
            
            DOMAINDISKUSED = 0
            for dom in DOMAININFO:
                DOMAINDISKUSED += dom['disks_sum']                      

            raw_resurces = { HOSTNAME: {'cpu_model': NODEEXECINFO[0],
                                        'vnet_count': VNETCOUNT,
                                        'cpu_sockets': NODEINFO['cpu_sockets'],
                                        'total_cpus': NODEINFO['cpus'],
                                        'threads_per_core': NODEINFO['threads_per_core'],
                                        'total_memory_size': re.sub(r'[^\d]','',NODEINFO['memory_size']),
                                        'domains_cpu_used': sum(DOMAINS_CPU_USED),
                                        'domains_memory_used':sum(DOMAINS_MEMORY_USED),
                                        'domains_disk_used':DOMAINDISKUSED,
                                        'disks': NODEDISKS,
                                        'domains': DOMAININFO
                } }
        return raw_resurces
    except unix.UnixError as e:
        raise Exception(f'{e} for {kvm_node}')

print(_inspector(kvm_node='virt07.lenvendo.ru'))
