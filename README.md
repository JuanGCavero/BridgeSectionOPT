# Parametric design and structural analysis for the optimization of bridge cross-sections.

In order to obtain a higher efficiency when designing and analyzing infrastructures, the transfer of geometry between Revit and Sofistik is solved by means of Dynamo and Python scripts for the case of railway bridges. Bridge cross-section are optimized using Genetic Algorithms.

## Prerequesites

Software:

* Revit 2020 or above
* Sofistik 2018 or above
* Python 3

Dynamo Packages:

* Clockwork for Dynamo 2.x
* Data-shapes
* Sofilink 2

## Setup and sample workflow

The repository contains two folders: Linking Framework and Optimization, with sample test workflows.

The Linking Framework allows the transfer of dimensional parameters from Revit to Sofistik, so that we can define a railway bridge within a UI (Data-Shapes) in Revit and analyze it with Sofistik automatically.
A handout (PDF) with the necessary instructions to perform the Linking process (Revit - Sofistik) is contained in the Repostitory.
There is also a [video tutorial](https://www.youtube.com/watch?v=T_vnRhejjgo&feature=youtu.be).

The Optimization, in a simillar way, contains Dynamo scripts to define the bridge and GA parameters. This data is stored in the workspace. Then a python script retrieves this data in order to perform the Genetic Optimization. For the evaluation process, results from Sofistik's analysis are used.

## Authors

* **Juan González Cavero**

## Acknowledgments

* **Jan Frölich**
* **Felipe Trovatti**

who along with me developed the Sofilink Dynamo package as part of a university project (Weimar, 2019).
