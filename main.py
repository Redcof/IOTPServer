import commands as cmd


if __name__ == "__main__":
	_version_ = "1.0.0"
	print "Welcome to IOTP server version " + _version_
	
	while True:
		u_cmd = raw_input("IOTP server:"+_version_+" >>> ")
		u_cmd_comp = u_cmd.split(" ")
		component = cmd._cmd_map[u_cmd_comp[0]]
		u_cmd_comp.pop(0)	
		if component:
			component[1](u_cmd_comp)
		elif u_cmd == "exit":
			break;
		else:
			cmd._cmd_map["-h"][1]()
		
	print "Exiting IOTP server..."
	
	print "OK"