from pysnmp.hlapi import *
import tkinter as tk

def snmp_get(ip, oid, community):
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

def snmp_set(ip, oid, value, community):
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


def snmp_getnext(ip, oid, community):
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

def choose_operation(operation):
    community = community_entry.get()
    if operation == 'GET':
        snmp_get(ip_address.get(), oid_entry.get(), community)
    elif operation == 'SET':
        snmp_set(ip_address.get(), oid_entry.get(), value_entry.get(), community)
    elif operation == 'GETNEXT':
        snmp_getnext(ip_address.get(), oid_entry.get(), community)

def main():
    global ip_address, oid_entry, value_entry, log_text, community_entry

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

    get_button = tk.Button(root, text="GET", command=lambda: choose_operation('GET'))
    get_button.grid(row=4, column=0)

    set_button = tk.Button(root, text="SET", command=lambda: choose_operation('SET'))
    set_button.grid(row=4, column=1)

    getnext_button = tk.Button(root, text="GETNEXT", command=lambda: choose_operation('GETNEXT'))
    getnext_button.grid(row=4, column=2)

    log_text = tk.Text(root, width=50, height=10)
    log_text.grid(row=5, columnspan=3)

    root.mainloop()

if __name__ == "__main__":
    main()
