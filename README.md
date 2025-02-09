Based on ![this researchpaper](https://www.nature.com/articles/s41598-023-31658-w)

***rebuilding checklist based on memory***


- [x] identify features to extract from pgn games
- [x] create a script to parse pgn files
- [x] design functions to collect feature data
- [x] create scoring system for playstyle (aggression, defensiveness, tactics)
  
- [x] collect games of players rated between 1400-2000 over a one year period
- [] create bipartitie network of players and openings based on scoring system of extracted from games
- [] project BpN to show how openings are shared across multiple players (signifying an opening repertoire and a relationship to playstyle)
- [] identify significance of connections, re-evaluate features and scoring if needed.
- [] research clustering algorithms, apply best fit
- [] research recommendation models, apply best fit
- [] verify accuracy of model by comparing results to actual openings of players (including newly added openings, not part of train or test datasets)


- [] design website that allows for username input, accesses pgn files for that user, determines playstyle and then recommends openings

