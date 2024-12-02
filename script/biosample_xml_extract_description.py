import xml.sax
import sys
import re


class XMLHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.init_current_sample()
        self.tag_stack = []

    def init_current_sample(self):
        self.current_bsid = ""
        self.current_descs = []
        self.current_content = ""
        self.current_db = ""
        self.current_title = ""
        self.current_tax_id = ""
        self.current_tax_name = ""

    def startElement(self, tag, attrs):
        self.tag_stack.append(tag)

        if tag == "BioSample":
            self.init_current_sample()
        if self.tag_stack == ["BioSampleSet", "BioSample", "Ids", "Id"]:
            if attrs.__contains__("db"):
                self.current_db = attrs.getValue("db")
        elif self.tag_stack == ["BioSampleSet", "BioSample", "Description", "Title"]:
            self.current_attr_name = "Title"
        elif self.tag_stack == ["BioSampleSet", "BioSample", "Description", "Organism"]:
            self.current_attr_name = "Organism"
            if attrs.__contains__("taxonomy_id"):
                self.current_tax_id = attrs.getValue("taxonomy_id")
            if attrs.__contains__("taxonomy_name"):
                self.current_tax_name = attrs.getValue("taxonomy_name")
        elif self.tag_stack == ["BioSampleSet", "BioSample", "Description", "Paragraph"]:
            if attrs.__contains__("label"):
                self.current_link_label = attrs.getValue("label")

    def characters(self, content):
        self.current_content += content.strip()

    def endElement(self, tag):
        if self.tag_stack == ["BioSampleSet", "BioSample", "Ids", "Id"]:
            if self.current_db == "BioSample":
                self.current_bsid = self.current_content
                self.current_db = ""
        elif self.tag_stack == ["BioSampleSet", "BioSample", "Description", "Title"]:
            self.current_title = self.current_content
        elif self.tag_stack == ["BioSampleSet", "BioSample", "Description", "Comment", "Paragraph"]:
            self.current_descs.append(self.current_content)

        if self.tag_stack == ["BioSampleSet", "BioSample"]:
            for desc in self.current_descs:
                print(self.current_bsid, "Comment", desc, sep="\t")
            print(self.current_bsid, "Title", self.current_title, sep="\t")
            print(self.current_bsid, "taxonomy_id", self.current_tax_id, sep="\t")
            print(self.current_bsid, "taxonomy_name", self.current_tax_name, sep="\t")
        self.tag_stack.pop()
        self.current_content = ""


def extract_text_to_tsv(xml_file):
    handler = XMLHandler()
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    parser.parse(xml_file)


input_xml = sys.argv[1]
extract_text_to_tsv(input_xml)
