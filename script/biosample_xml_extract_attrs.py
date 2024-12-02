import xml.sax
import sys
import re


class XMLHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.init_current_sample()
        self.tag_stack = []

    def init_current_sample(self):
        self.current_bsid = ""
        self.current_content = ""
        self.current_db = ""
        self.current_link_label = ""
        self.current_link_target = ""
        self.current_attr_name = ""

    def startElement(self, tag, attrs):
        self.tag_stack.append(tag)

        if tag == "BioSample":
            self.init_current_sample()

        if self.tag_stack == ["BioSampleSet", "BioSample", "Ids", "Id"]:
            if attrs.__contains__("db"):
                self.current_db = attrs.getValue("db")
        elif self.tag_stack == ["BioSampleSet", "BioSample", "Attributes", "Attribute"]:
            self.current_attr_name = attrs.getValue("attribute_name")

    def characters(self, content):
        self.current_content += content.strip()

    def endElement(self, tag):
        if self.tag_stack == ["BioSampleSet", "BioSample", "Ids", "Id"]:
            if self.current_db == "BioSample":
                self.current_bsid = self.current_content
            self.current_db = ""

        elif self.tag_stack == ["BioSampleSet", "BioSample", "Attributes", "Attribute"]:
            # self.current_attrs[self.current_attr_name] = self.current_content
            print(self.current_bsid, self.current_attr_name, self.current_content, sep="\t")

        self.tag_stack.pop()
        self.current_content = ""


def extract_text_to_tsv(xml_file):
    handler = XMLHandler()
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    parser.parse(xml_file)


input_xml = sys.argv[1]
extract_text_to_tsv(input_xml)
