## LSU Wheat Internal Site Code

Code for internal LSU AgCenter small grains breeding site hosting various tools for germplasm management. The core code is a Django site over an SQLite database for family-based tracking of crosses and germplasm plots and seed stocks. HTMX is used to provide some limited reactivity for CRUD applications, while more involved interfaces are built with R Shiny apps that directly load the SQLite db file. This is designed to supplement Breedbase for management of crossing and early generations in a bulk pedigree wheat breeding program. The input should be accession information exported from Breedbase, used to generate segregating early-generation populations that undergo cyles of selection and re-generation of derived populations, and have as a final outcome a list of new accessions to enter into Breedbase. The crossing applications and label generation tools are designed to work with the PhenoApps Intercross app for cross recording and status updating. At the moment, the tools for crossing and associated seedlot management are the only fully developed tools, while tools for headrow harvest/selection are still a work in progress.

This is mostly for my own personal backup/version control, but if you have any interest in adapting it, feel free to reach out at NDeWitt@agcenter.lsu.edu. The Shiny applications are designed to work with the SQLite data models, but should be fairly easy to modify to load similar data from local sources.


### Screenshots
#### Crossing App
![image](https://github.com/noahddewitt/LSU_SGrains_tools/assets/82885768/6af14ce8-e622-4600-b217-38e3f0dd8bf2)

#### Crossing Page
![image](https://github.com/noahddewitt/LSU_SGrains_tools/assets/82885768/0e99e35e-2fd2-41f5-9f2e-23d706a8e17a)

#### Cross Detail
![image](https://github.com/noahddewitt/LSU_SGrains_tools/assets/82885768/d22f2044-e9d9-466d-8f8f-06497ee8762b)

#### Cross Status Shiny App
![image](https://github.com/noahddewitt/LSU_SGrains_tools/assets/82885768/8d9d91ca-037d-4cc3-ac1d-55edaf54634a)

#### Family Pages
![image](https://github.com/noahddewitt/LSU_SGrains_tools/assets/82885768/a26a5e21-69a0-4476-b58f-9ec167801ead)

#### Label Tool
![image](https://github.com/noahddewitt/LSU_SGrains_tools/assets/82885768/4671fac1-2e49-42cc-a686-99ce5d77d1e5)

#### Nursery Generation
![image](https://github.com/noahddewitt/LSU_SGrains_tools/assets/82885768/78492d19-ce88-4766-9a06-29d92f5fdbc4)



