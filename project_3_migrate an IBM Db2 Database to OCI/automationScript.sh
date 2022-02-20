#!/bin/bash
echo "Threat Profiling Automation Script by Jahidul Arafat"
echo ">> Generating Data Flow Diagram"
./main.py --dfd | dot -Tpng -o outputs/dfd.png

echo ">> Generating Sequence Diagram"
./main.py --seq | java -Djava.awt.headless=true -jar ../resources/plantuml.jar -tpng -pipe > outputs/seq.png

echo ">> Generating Total Threat Profile Report"
./main.py --report ../resources/my_templates/basic_template.md | pandoc -f markdown -t html > outputs/report.html
