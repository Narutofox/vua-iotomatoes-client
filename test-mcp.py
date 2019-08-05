import mcp3008

m = mcp3008.read_pct(0)

print("Maisture level: {:>5}".format(m))