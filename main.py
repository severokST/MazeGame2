from engine import Map
from gui import GUIWindow



map = Map()
map.print_graph()

window = GUIWindow()
window.map.map_local(map)
window.run()











