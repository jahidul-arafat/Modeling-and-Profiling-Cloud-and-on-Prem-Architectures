<!DOCTYPE html>
<html>
<head>
<p><link rel="stylesheet" href="../../resources/my_templates/Stylesheet.css"></p>
</head>
<body>

<img src="../../resources/my_templates/oci_banner.png" alt="Oracle Cloud Infrastructure" width="100%" height="50%">


## Project Name: {tm.name}

## OCI Reference Architecture
<img src="../oci_reference_architecture/ibmdb-to-adb.svg" alt="OCI Reference Architecture">


---

## System Description

{tm.description}

---

{tm.assumptions:if:
|Assumptions|
|:-----------:|
{tm.assumptions:repeat:|{{item}}| 
}}


## Dataflow Diagram - Level 0 DFD
![](../../project_3_migrate\ an\ IBM\ Db2\ Database\ to\ OCI//outputs/dfd.png)

## Sequence Diagram
![](../../project_3_migrate\ an\ IBM\ Db2\ Database\ to\ OCI//outputs/seq.png)

&nbsp;

## Dataflows
Name|From|To |Data|Protocol|Port
|:----:|:----:|:---:|:----:|:--------:|:----:|
{dataflows:repeat:|{{item.name}}|{{item.source.name}}|{{item.sink.name}}|{{item.data}}|{{item.protocol}}|{{item.dstPort}}|
}

## Data Dictionary
Name|Description|Classification|Carried|Processed
|:----:|:--------:|:----:|:----:|:----:|
{data:repeat:|{{item.name}}|{{item.description}}|{{item.classification.name}}|{{item.carriedBy:repeat:{{{{item.name}}}}<br>}}|{{item.processedBy:repeat:{{{{item.name}}}}<br>}}|
}


## Potential Threats

|{findings:repeat:
<details>
  <summary>   {{item.threat_id}}   --   {{item.description}}</summary>
  <h6> Targeted Element </h6>
  <p> {{item.target}} </p>
  <h6> Severity </h6>
  <p>{{item.severity}}</p>
  <h6>Example Instances</h6>
  <p>{{item.example}}</p>
  <h6>Mitigations</h6>
  <p>{{item.mitigations}}</p>
  <h6>References</h6>
  <p>{{item.references}}</p>
  &nbsp;
  &nbsp;
  &emsp;
</details>
}|

</body>
</html>
