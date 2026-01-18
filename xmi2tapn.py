import xml.etree.ElementTree as ET
import math
from xml.dom import minidom

def create_tapaal_tapn(xmi_filename, output_filename):
    try:
        tree = ET.parse(xmi_filename)
        root = tree.getroot()
    except Exception as e:
        print(f"Error loading XMI file: {e}")
        return

    # Extract Places and Transitions from XMI
    places = []
    transitions = []
    arcs = []
    
    # XMI format: <places name="Tile1" tokens="1"/>
    for elem in root:
        if "places" in elem.tag:
            p_name = elem.attrib.get("name", f"P{len(places)}")
            p_tokens = elem.attrib.get("tokens", "0")
            p_id = f"P{len(places)}"
            places.append({"id": p_id, "name": p_name, "tokens": p_tokens})

    # XMI format: <transitions input="//@places.0" output="//@places.1" ... />
    t_count = 0
    arc_count = 0
    for elem in root:
        if "transitions" in elem.tag:
            t_id = f"T{t_count}"
            t_name = elem.attrib.get("name", t_id)
            transitions.append({"id": t_id, "name": t_name})
            
            # Helper to parse references like "//@places.0"
            def parse_refs(ref_string):
                indices = []
                if not ref_string: return indices
                for ref in ref_string.split():
                    try:
                        # Extract the number after the dot
                        idx = int(ref.split(".")[-1])
                        indices.append(idx)
                    except: pass
                return indices

            # Input Arcs (Place -> Transition)
            inputs = parse_refs(elem.attrib.get("input", ""))
            for p_idx in inputs:
                if p_idx < len(places):
                    arcs.append({
                        "id": f"A{arc_count}",
                        "source": places[p_idx]["id"],
                        "target": t_id
                    })
                    arc_count += 1

            # Output Arcs (Transition -> Place)
            outputs = parse_refs(elem.attrib.get("output", ""))
            for p_idx in outputs:
                if p_idx < len(places):
                    arcs.append({
                        "id": f"A{arc_count}",
                        "source": t_id,
                        "target": places[p_idx]["id"]
                    })
                    arc_count += 1
            t_count += 1


    # TAPAAL requires a specific namespace and declaration block
    pnml = ET.Element("pnml", xmlns="http://www.informatik.hu-berlin.de/top/pnml/ptNetb")
    
    # <declaration> block
    decl = ET.SubElement(pnml, "declaration")
    struct = ET.SubElement(decl, "structure")
    decls = ET.SubElement(struct, "declarations")
    # Define the "dot" type
    ns = ET.SubElement(decls, "namedsort", id="dot", name="dot")
    ET.SubElement(ns, "dot")

    # <net> block
    net = ET.SubElement(pnml, "net", active="true", id="TAPN1", type="P/T net")

    # Layout Calculations
    cx, cy, r = 400, 400, 300
    angle_step = (2 * math.pi) / (len(places) + len(transitions)) if (len(places) + len(transitions)) > 0 else 0
    current_angle = 0
    
    def get_pos(angle):
        return str(int(cx + r * math.cos(angle))), str(int(cy + r * math.sin(angle)))

    # WRITE PLACES
    for p in places:
        x, y = get_pos(current_angle)
        p_elem = ET.SubElement(net, "place", 
                               displayName="true", 
                               id=p["id"], 
                               initialMarking=p["tokens"], 
                               invariant="< inf", 
                               name=p["name"], 
                               nameOffsetX="0", nameOffsetY="0", 
                               positionX=x, positionY=y)
        

        type_elem = ET.SubElement(p_elem, "type")
        ET.SubElement(type_elem, "text").text = "dot"
        s_elem = ET.SubElement(type_elem, "structure")
        ET.SubElement(s_elem, "usersort", declaration="dot")
        
        current_angle += angle_step

    # WRITE TRANSITIONS
    for t in transitions:
        x, y = get_pos(current_angle)
        ET.SubElement(net, "transition", 
                      angle="0", 
                      displayName="true", 
                      id=t["id"], 
                      infiniteServer="false", 
                      name=t["name"], 
                      nameOffsetX="0", nameOffsetY="0", 
                      player="0", 
                      positionX=x, positionY=y, 
                      priority="0", 
                      urgent="false", 
                      weight="1.0")
        current_angle += angle_step

    # WRITE ARCS
    for a in arcs:
        # Check if source starts with 'T' (Transition) to identify Output Arcs
        is_output = a["source"].startswith("T")

        if is_output:
            # Transition -> Place (Output Arc)
            arc_inscription = "1"
            arc_type = "normal"
        else:
            # Place -> Transition (Input Arc)
            arc_inscription = "[0,inf)"
            arc_type = "timed"

        arc_elem = ET.SubElement(net, "arc",
                                 id=a["id"],
                                 inscription=arc_inscription,
                                 nameOffsetX="0", nameOffsetY="0",
                                 source=a["source"],
                                 target=a["target"],
                                 type=arc_type,
                                 weight="1")

        hl = ET.SubElement(arc_elem, "hlinscription")
        ET.SubElement(hl, "text").text = "1'dot"
        hl_struct = ET.SubElement(hl, "structure")
        num_of = ET.SubElement(hl_struct, "numberof")

        sub1 = ET.SubElement(num_of, "subterm")
        nc = ET.SubElement(sub1, "numberconstant", value="1")
        ET.SubElement(nc, "positive")

        sub2 = ET.SubElement(num_of, "subterm")
        ET.SubElement(sub2, "useroperator", declaration="dot")

    ET.SubElement(pnml, "feature",
                  isColored="false",
                  isGame="false",
                  isStochastic="false",
                  isTimed="false")


	# Save file
    raw_string = ET.tostring(pnml, encoding='utf-8')
    parsed = minidom.parseString(raw_string)
    pretty_xml = parsed.toprettyxml(indent="  ")

    with open(output_filename, "w") as f:
        f.write(pretty_xml)
        
    print(f"Conversion Complete! File saved as: {output_filename}")

# Run
create_tapaal_tapn("TransformedPetriNet.xmi", "TransformedPetriNet.tapn")
