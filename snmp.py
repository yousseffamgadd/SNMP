from pysnmp.hlapi import *
import tkinter as tk
import smtplib
import subprocess
import time

previous_uptime = {}

def snmp_get(ip, oid, community, log_text):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    )
    if errorIndication:
        log_text.insert(tk.END, f"Error: {errorIndication}\n")
    elif errorStatus:
        log_text.insert(tk.END, f"Error: {errorStatus.prettyPrint()}\n")
    else:
        for varBind in varBinds:
            log_text.insert(tk.END, ' = '.join([x.prettyPrint() for x in varBind]) + "\n")

def snmp_set(ip, oid, value, community, log_text):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        setCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid), OctetString(value)))
    )
    if errorIndication:
        log_text.insert(tk.END, f"Error: {errorIndication}\n")
    elif errorStatus:
        log_text.insert(tk.END, f"Error: {errorStatus.prettyPrint()}\n")
    else:
        log_text.insert(tk.END, "Set successful\n")

def snmp_getnext(ip, oid, community, log_text):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        nextCmd(SnmpEngine(),
                CommunityData(community),
                UdpTransportTarget((ip, 161)),
                ContextData(),
                ObjectType(ObjectIdentity(oid)))
    )
    if errorIndication:
        log_text.insert(tk.END, f"Error: {errorIndication}\n")
    elif errorStatus:
        log_text.insert(tk.END, f"Error: {errorStatus.prettyPrint()}\n")
    else:
        for varBind in varBinds:
            log_text.insert(tk.END, ' = '.join([x.prettyPrint() for x in varBind]) + "\n")

def monitor_uptime(root, ip, community, threshold, log_text):
    global previous_uptime

    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity('1.3.6.1.2.1.1.3.0')))
    )
    if errorIndication:
        log_text.insert(tk.END, f"Error: {errorIndication}\n")
    elif errorStatus:
        log_text.insert(tk.END, f"Error: {errorStatus.prettyPrint()}\n")
    else:
        current_uptime_ticks = int(varBinds[0][1])
        current_uptime_seconds = current_uptime_ticks / 100  # SNMP uptime is in hundredths of a second
        uptime_days = current_uptime_seconds // (24 * 3600)
        uptime_hours = (current_uptime_seconds % (24 * 3600)) // 3600
        uptime_minutes = (current_uptime_seconds % 3600) // 60
        uptime_seconds = current_uptime_seconds % 60
        log_text.insert(tk.END, f"Current System Uptime for IP {ip}: {int(uptime_days)} days, {int(uptime_hours)} hours, {int(uptime_minutes)} minutes, {int(uptime_seconds)} seconds\n")

        if current_uptime_seconds >= threshold:
            if current_uptime_seconds > previous_uptime.get(ip, 0) + 10:
                log_text.insert(tk.END, "Threshold Exceeded! Running script...\n")
                try:
                    if ip == "192.168.1.21":
                        subprocess.run(["/home/kali/Desktop/send.sh"], check=True)
                    elif ip == "192.168.1.13":
                        subprocess.run(["/home/kali/Desktop/send2.sh"], check=True)
                    else:
                        log_text.insert(tk.END, "No script specified for this IP.\n")
                except subprocess.CalledProcessError as e:
                    log_text.insert(tk.END, f"Error running script: {e}\n")
                else:
                    log_text.insert(tk.END, "Script executed successfully!\n")

        previous_uptime[ip] = current_uptime_seconds
        root.after(threshold * 1000, monitor_uptime, root, ip, community, threshold, log_text)



def choose_operation(operation, ip_address, oid_entry, value_entry, community_entry, log_text):
    community = community_entry.get()
    if operation == 'GET':
        snmp_get(ip_address.get(), oid_entry.get(), community, log_text)
    elif operation == 'SET':
        snmp_set(ip_address.get(), oid_entry.get(), value_entry.get(), community, log_text)
    elif operation == 'GETNEXT':
        snmp_getnext(ip_address.get(), oid_entry.get(), community, log_text)

def main():
    root = tk.Tk()
    root.title("SNMP Manager")

    ip_label = tk.Label(root, text="IP Address:")
    ip_label.grid(row=0, column=0)
    ip_address = tk.Entry(root)
    ip_address.grid(row=0, column=1)

    oid_label = tk.Label(root, text="OID:")
    oid_label.grid(row=1, column=0)
    oid_entry = tk.Entry(root)
    oid_entry.grid(row=1, column=1)

    value_label = tk.Label(root, text="Value (for SET):")
    value_label.grid(row=2, column=0)
    value_entry = tk.Entry(root)
    value_entry.grid(row=2, column=1)

    community_label = tk.Label(root, text="Community:")
    community_label.grid(row=3, column=0)
    community_entry = tk.Entry(root)
    community_entry.grid(row=3, column=1)


    get_button = tk.Button(root, text="GET", command=lambda: choose_operation('GET', ip_address, oid_entry, value_entry, community_entry, log_text))
    get_button.grid(row=5, column=0)

    set_button = tk.Button(root, text="SET", command=lambda: choose_operation('SET', ip_address, oid_entry, value_entry, community_entry, log_text))
    set_button.grid(row=5, column=1)

    getnext_button = tk.Button(root, text="GETNEXT", command=lambda: choose_operation('GETNEXT', ip_address, oid_entry, value_entry, community_entry, log_text))
    getnext_button.grid(row=5, column=2)
    
    ip_addresses = ["192.168.1.13", "192.168.1.21"]
    communities = ["HELLO", "READ"]
    thresholds = [6, 12]

    log_text = tk.Text(root, width=50, height=10)
    log_text.grid(row=7, columnspan=3)

    # Monitor uptime for each IP address
    for ip, community, threshold in zip(ip_addresses, communities, thresholds):
        monitor_uptime(root, ip, community, threshold, log_text)

    root.mainloop()

if __name__ == "__main__":
    main()
