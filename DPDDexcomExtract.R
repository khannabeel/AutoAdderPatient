# Database Dexcom Extraction
library(tidyverse)

# Select columns with needed CGM information
cgmunsorted <- read.delim("20220719dpdcgm.tsv") 
cgmunsorted <- as_tibble(cgmunsorted)
cgmdexcom <- cgmunsorted %>% filter(str_detect(cgm_flash_dosage, "excom"))
cgmdexemail <- cgmdexcom %>% filter(str_detect(email, "@"))
cgmdexemailfl <- cgmdexemail %>% select('name_first', 'name_last', 'dob', 'email') %>% na.omit()
cgmdexemailfl <- cgmdexemailfl %>% separate(dob, c('year', 'month', 'date'), sep='-')

cgmdexemailfl <- cgmdexemailfl %>% mutate(month = month.name[as.integer(month)])

write_delim(cgmdexemailfl, 'dpdcgm.tsv', delim = '\t', col_names = FALSE)
