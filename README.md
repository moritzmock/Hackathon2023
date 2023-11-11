# CosmicCarots

## Intro

This is a powerful tool crafted to empower farmers and agriculturists with comprehensive insights for their fields. Harnessing the strength of cutting-edge data analysis and visualization, our application is designed to transform raw data into meaningful, visually intuitive knowledge.


## Project Description
As we all know, it is the dream of every South Tyrolean farmer to watch its carrots grow from the cosmos. We, the CosmicCarrots team, have made it our goal to no longer leave this wish unfulfilled. However, Konverto's satellite data offers so much more for farmers than just showing their fields on orthophotos. 

In fact, it can give them valuable insights about how climate change is affecting their fields over time, when the best time to harvest will come and how their fields will develop in comparison to neighbouring fields. 

Through our user interface, farmers can simply enter the parcel numbers of their agricultural land and our application will calculate weather data as well as specific agricultural indices (NDWI, NDVI, GDD) for that parcel to give farmers high-resolution insights to make work and organization easier.


## Key Features
- Data Visualization: Unleash the potential of agricultural data through interactive and informative visualizations. Gain a deeper understanding of fields with graphs, charts, and maps that make complex information easy to grasp.

- Machine Learning: The project also involves some lightweight machine learning models that help to impute missing values in the data and to forecast the GDD.



## Installation
Use the provided [environment.yml](./environment.yml) file to install all the dependencies with the conda package manager.

To run the notebook [plot_map_final](./visualize_data/plot_map_final.ipynb) it is necessary to do some preparatory steps: The Git repository for this project does not include the underlying data, as it is not publicly available. To run the notebooks and the code effectively, you need to place the "konverto_data_package" in the same directory as the project's main folder, which is one level above the project's Git root. Additionally, for the data visualization component to work, you must precompute the 'csv_dump' file and save it in the 'visualize_data' folder.


## Usage
To run the plot_map_final notebook follow first the installation by saving the raw data in the correct folder. After that it is possible to open the juypter notebooks and run the code. In order to run the data visualisation notebook it is necessary to precompute csv_dumps from the data_extraction.ipynb notebook in the data extraction folder.


To launch the dashboard web application change directory into the dashboard sub-folder and then run the following command in the terminal:

> python ./dashboard.py




## Authors
Borsani, Thomas
Di Panfilo, Marco 
Mock, Moritz
Rabensteiner, Jonas