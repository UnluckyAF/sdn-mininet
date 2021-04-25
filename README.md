# Запуск

    run VirtualBox
    start Mininet-VM
    login + password mininet

    ---

    ssh -Y mininet@mininet-vm - подключаемся из двух терминалов
    pox/pox.py --verbose openflow.spanning_tree --no-flood --hold-down log.level --DEBUG samples.pretty_log openflow.discovery forwarding.l2_multi info.packet_dump -
    запускаем контроллер на одном терминале 

    sudo python ~/mininet/custom/hard_topo.py ИЛИ
    sudo mn --custom ~/mininet/custom/hard_topo.py --topo mytopo --controller remote --switch ovsk --mac - запускаем сам
    mininet с нужной топологией

Если запустить pox как выше, потом mininet, подождать spanning tree, пустить pingall, выключить pox, запустить снова как выше, подождать spanning tree, пустить pingall - все пинги проходят

## Запуск серверов (!!!will be changed!!!)

    mininet запустить как выше с опцией -x - откроются окна каждого хоста
    (касается только запуска hard_topo) для 9 хостов запустить обычный сервер, для одного с опцией --init


# Полезные ссылки

<http://mininet.org/walkthrough/>  
<http://pld.cs.luc.edu/courses/netmgmt/sum17/notes/mininet_and_pox.html>
