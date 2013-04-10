from xml.dom.minidom import parse, parseString

dom = parse( "myCity.xml" )
print (dom.toxml())