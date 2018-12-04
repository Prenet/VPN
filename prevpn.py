#!/usr/bin/env python


import requests, os, sys, tempfile, subprocess, base64, time


if len(sys.argv) != 2:
    print 'usage: prevpn.py [nome do pais | codigo do pais]'
    exit(1)
country = sys.argv[1]

if len(country) == 2:
    i = 6 # short name for country
elif len(country) > 2:
    i = 5 # long name for country
else:
    print 'Pais e muito curto!'
    exit(1)

try:
    vpn_data = requests.get('http://www.vpngate.net/api/iphone/').text.replace('\r','')
    servers = [line.split(',') for line in vpn_data.split('\n')]
    labels = servers[1]
    labels[0] = labels[0][1:]
    servers = [s for s in servers[2:] if len(s) > 1]
except:
    print 'Nao e possivel obter dados dos servidores VPN'
    exit(1)

desired = [s for s in servers if country.lower() in s[i].lower()]
found = len(desired)
print 'Encontrado ' + str(found) + ' servidores do pais ' + country
if found == 0:
    exit(1)

supported = [s for s in desired if len(s[-1]) > 0]
print str(len(supported)) + ' desses servidores suportam o OpenVPN'
# We pick the best servers by score
winner = sorted(supported, key=lambda s: float(s[2].replace(',','.')), reverse=True)[0]

print "\n== Melhor Servidor =="
pairs = zip(labels, winner)[:-1]
for (l, d) in pairs[:4]:
    print l + ': ' + d

print pairs[4][0] + ': ' + str(float(pairs[4][1]) / 10**6) + ' MBps'
print "Estado: " + pairs[5][1]

print "\nAbrindo VPN..."
_, path = tempfile.mkstemp()

f = open(path, 'w')
f.write(base64.b64decode(winner[-1]))
f.write('\nscript-security 2\nup /etc/openvpn/update-resolv-conf\ndown /etc/openvpn/update-resolv-conf')
f.close()

x = subprocess.Popen(['sudo', 'openvpn', '--config', path])

try:
    while True:
        time.sleep(600)
# termination with Ctrl+C
except:
    try:
        x.kill()
    except:
        pass
    while x.poll() != 0:
        time.sleep(1)
    print '\nVPN terminou'
