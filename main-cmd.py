from IOTP_CommandLine import commands as cmd

if __name__ == "__main__":
    _version_ = "1.0.0"
    print "Welcome to IOTP server version " + _version_

    while True:
        try:
            u_cmd = raw_input("IOTP server:" + _version_ + " >>> ")
            # Split the command string
            u_cmd_component = u_cmd.split(" ")
            # filter all empty component form list
            u_cmd_component = filter(None, u_cmd_component)
            # get the first component as the COMMAND
            component = cmd.cmd_map[u_cmd_component[0]]
            # remove the COMMAND form the list
            u_cmd_component.pop(0)
            print u_cmd_component
            if component:
                component[1](u_cmd_component)
            elif u_cmd == "exit":
                break
            else:
                cmd.cmd_map["-h"][1]()
        except:
            break
    print "Exiting IOTP server..."

    print "OK"
