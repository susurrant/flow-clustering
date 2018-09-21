# flow-clustering

## Description
Flow clustering, which summarizes individual flows into aggregate flows, can help to discover human mobility patterns. Existing flow clustering methods ignore the geometric properties of flows and do not consider their temporal information. This research</br>
1. Defines new measurements of spatial similarity and temporal similarity between flows.</br>
2. Develops a spatio-temporal clustering method for flow data.</br>

## Enviroment
Python version: 3.5 (some codes were written using 2.7)</br>

## Reference
> [A Stepwise Spatio-Temporal Flow Clustering Method for Discovering Mobility Trends](https://ieeexplore.ieee.org/document/8432425/)</br>
> Xin Yao, Di Zhu, Yong Gao, *et al.*, 2018, IEEE Access</br>

## Method
- **Spatial similarity:** (a) Flows are in spatial proximity to each other. (b) Flow directions are approximately equivalent. (c) Flow lengths are similar.</br>
- **Temporal Similarity:** Two flows are more temporally similar if the periods during which they occur overlap more.</br>
- **Algorithms:** We use a two-step clustering strategy in which spatial clustering is conducted before temporal clustering. An agglomerative clustering framework is adopted to implement flow clustering, which merges flows to form a hierarchy of flow clusters.</br>

## Example
We apply the method to Beijing taxi trip data, which contains valid 266,817 records from 17,397 different taxis on May 13, 2013. </br>
1. Data:</br>
![data](data.jpg)
2. Spatial clustering:</br>
![spatial clustering](spatial_clustering.jpg)
3. Temporal clustering of spatial clusters #151 and #318:</br>
![temporal clustering](temporal_clustering.jpg)