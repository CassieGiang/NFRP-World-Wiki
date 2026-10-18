# Ninja ranks and the rank exam
Every ninja can climb four ranks: **genin**, **chūnin**, **jōnin** and **village leader**. A rank shows as a small bonus on the pawn's health tab, and each one replaces the last.

## The rank exam
Every couple of weeks the **rank exam** event comes round, as long as at least one colonist is eligible. Each eligible ninja sits the exam for the next rank. The chance of passing starts at 55%, goes up 4% for every ninja level above the requirement, and always stays between 30% and 92%. Passing gives a good mood for ten days; failing gives a small dip for five, and they can try again next time.

- **Genin**: needs ninja level 3. Bonus: learns a little faster.
- **Chūnin**: needs a year (60 days) as genin, level 8, and Melee or Shooting 6. Bonus: learns faster, more social impact, steadier nerves.
- **Jōnin**: needs two years (120 days) as chūnin, level 13, and two of Melee, Shooting, Intellectual or Medicine at 8. Bonus: social impact, steadier nerves, better aim and melee hits.
- **Village leader**: needs four years (240 days) as jōnin, level 16 and Social 8; only one per colony. Bonus: big social and negotiation bonus, steady nerves, better aim and hits.

Hover over a rank on the health tab to see the pawn's ninja level, how long they've held the rank, what the next exam needs, and whether they're ready for it.

**Ninja level** is the highest of the pawn's Ninjutsu, Taijutsu and Genjutsu class levels.

## Leveling pace
Ninja classes level slowly, so a rank is earned over years of play:

- Each new level of Ninjutsu, Taijutsu or Genjutsu costs 150 × (current level + 1) XP, three times the framework's default. Reaching level 20 takes 31,500 XP in all.
- NFRP World techniques give a small amount of XP once per cast, to the class the technique belongs to: D rank 1, C rank 3, B rank 4, A rank 7, S rank 11. Fighting alone won't make a jōnin.

## Other ways to grow
- **Training**: one session a day at a training building gives class XP as well as skill. Training post and training dummy: 15 Taijutsu. Battle ring: 18 Taijutsu. Chakra study apparatus ("Study chakra at"): 15 Ninjutsu. Star-watching platform ("Meditate on"): 15 Genjutsu. From class level 8 training gives half, and training alone stops at level 10. Pawns who refuse violence can't use the apparatus or the platform.
- **Sensei and student**: select a colonist below jōnin and use the **Sensei** button to pick a jōnin or village leader who outranks them. While the sensei is awake within 15 cells, the student gets three times the XP from training and sparring, in the sensei's best class, and can grow past level 10 up to one level below the sensei (at most 16). The sensei gains Social.
- **Sparring**: select a colonist, right-click a **battle ring** and pick "Spar with" a partner. Both walk to the ring and spar: Melee practice for both, 12 Taijutsu XP each at the end (three times as much with their sensei). There is a small chance of a light bruise; nobody gets knocked down.
- **Missions**: clearing a ranked mission's camp gives every ninja on the site class XP by mission rank: D 60, C 120, B 250, A 450, S 800.
- **Exams**: passing a rank exam gives genin 300, chūnin 600, jōnin 1,000 and village leader 1,500 class XP.

## Missions by rank
Like the role-play, a ninja's rank decides which missions they can take: unranked ninja only D, genin up to C, chūnin up to B, jōnin and the village leader any. Accepting a mission no ranked ninja of yours can take is refused with the reason. A colony with no ranked ninja at all is never blocked.

## The chūnin exam
About once a season after the truce ends, your sworn village (or another friendly village) invites your genin to the **chūnin exam**. Pick up to three genin and send them; the exam is played out at once in three stages:
- **Written test**: Intellectual and Social.
- **Survival trial**: ninja level and the better of Melee or Shooting.
- **Final duel**: ninja level, Melee and Shooting.

Each stage has a roll on both sides, so an underdog can win. Winners become **chūnin** on the spot, even without a year as genin, and gain 600 class XP; the others gain XP for how far they got (300, 150 or 60). Those beaten in the trial or the final may come back bruised. One letter tells the whole tournament, round by round, against genin from the other villages. The host's goodwill rises for every finalist and winner.

Ninja from other villages carry ranks too, matching how strong their loadout is: their leaders are village leaders, their elites jōnin.

In dev mode, the **NFRP World** debug actions include "Make selected pawn qualify for the next rank exam" (raises level, skills and time served to exactly what the next exam needs), "Rank exam now" (everyone eligible passes; if nobody is, it says why for each ninja), "Chūnin exam invitation now" and "Raise selected pawn's rank".
