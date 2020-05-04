# Tidy Tuesday Animal Crossing Data

Some rough high level groups have been made in `groups.csv`.

The main table is created with the snippet below.

```{r}
items = data.table::fread("https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2020/2020-05-05/items.csv")
groups = data.table::fread("groups.csv")
items = groups[items, on = "category"]
data.table::fwrite(items, "items.csv")

# Also json format
jsonlite::write_json(items, "../tidytuesday-items.json")
```
