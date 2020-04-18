# Animal Crossing Data

Thanks to [chendaniely](https://github.com/chendaniely)!

All critter data sourced from chendaniely's 
[animal_crossing](https://github.com/chendaniely/animal_crossing/tree/master/data) repo.

Note:

```
curl --silent https://raw.githubusercontent.com/chendaniely/animal_crossing/master/data/original/acnh_fish_n.tsv | jq --raw-input --slurp 'split("\n") | map(split("\t")) | .[0:-1] | map( { "Name": .[0], "Price": .[14] } )' > acnh_fish_n.json
```