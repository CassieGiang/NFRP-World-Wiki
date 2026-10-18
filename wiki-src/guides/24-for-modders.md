# For modders
What NFRP World patches, how its defs are named, and the extensions you can reuse.

This page is for people making mods that sit next to NFRP World, or tracking down a conflict. Players can skip it.

## Load order
- **Harmony**, then **Taran Magic Framework**, then **World of Naruto**, then **NFRP World**. NFRP World must load after both, because it adds trees to their framework and patches their classes.
- The mod supports RimWorld 1.6 and 1.7. On 1.7 it loads the same 1.6 folder (set in LoadFolders.xml), so there is one set of defs and one assembly for both.

## Seeing the live patch list
The startup line and the dev file come in the next update.

- At startup the log shows one line: **[NFRP World] Harmony patches: N on M methods**.
- For the full list, open the dev menu, go to **NFRP World**, and choose **List NFRP World patches**. It writes **NFRP_Patches.txt** to your RimWorld save-data folder (next to NFRP_SelfTest.txt), grouped by Harmony id. Each line gives the patch kind, the patched method and the NFRP method that does it.
- Every Harmony id starts with **cassie.nfrpworld.** so you can filter for them in any patch-listing tool.

## What gets patched, by system
The list below is current as of this page. The dev file above is always exact.

**Techniques and trees** (Taran Magic Framework)
- AbilityClass.LearnAbility and AbilityClass.RequiredXPForNewLevel: build limits and levelling pace.
- AcquireRequirement.RequirementSatisfied: tree unlock rules, with a finalizer (cassie.nfrpworld.reqguard) that stops a broken requirement from another mod throwing errors.
- CompAbilities.CompGetGizmosExtra: technique buttons, the tech UI and scribe scrolls.
- CompAbilities.PostDraw: aura effects.
- Ability.Start: projectile effects.

**Drawing and animation**
- PawnRenderer.GetDrawParms and PawnRenderer.ParallelGetPreRenderResults: cast poses and expansion visuals.
- Pawn.DrawPos, Pawn_DrawTracker.DrawPos, Notify_DamageApplied and Notify_MeleeAttackOn: hover, recoil and lunge.
- PawnRenderUtility.DrawEquipmentAiming: weapon effects.
- Projectile.Impact, ImpactSomething and TickInterval: projectile trails and hits.

**Crafting**
- Bill.PawnAllowedToStartAnew: alchemy, bloodline grafting, scribe and ritual items only let qualified pawns start a bill.
- GenRecipe.MakeRecipeProducts: alchemy modifiers and scrolls.
- RecipeDef.PawnSatisfiesSkillRequirements: weapon recipes.
- QualityUtility.GenerateQualityCreatedByPawn: passive quality bonuses.
- Thing.Ingested and Projectile_Explosive.Explode: alchemy items.

**Pawns and gear**
- PawnGenerator.GeneratePawn: faction gear and traits.
- Pawn.GetGizmos: alchemy, training and world job buttons.
- Pawn_HealthTracker.AddHediff: goggles and ideology hooks.
- Thing.TakeDamage: chakra seal.
- PrisonBreakUtility.CanParticipateInPrisonBreak: chakra-sealed prisoners.

**World, factions and quests**
- IncidentWorker.TryExecute and IncidentWorker_Raid.TryExecuteWorker: the faction war and the truce.
- FactionDialogMaker.FactionDialogFor: rank and diplomacy options.
- Quest.Accept and Quest.End: village contracts and ideology reactions.
- WeatherDecider.ChooseNextWeather: storm arts.

## Def names
- **NF_** for most defs: trees, abilities, hediffs, items, factions, rituals.
- **KZ_** for the Kazeraikou tree and its effects.
- **Weapon_NF_** for weapons and **Proj_NF_** for projectiles.
- Use these prefixes in XPath patches, for example to change a def without touching others.

## Extensions you can use
These are DefModExtensions in the CassieNFRP namespace. Add them to your own defs with the class attribute, for example li Class="CassieNFRP.NFRequiresTree".
- **NFRequiresTree** (on a recipe or item): tree, label. Only pawns who know that tree can make it.
- **NFDisciplineItem** (on an item): discipline. Ties an alchemy item to a discipline.
- **NFGeneTree** (on a tree): gene, abilityClass, parentTree. Unlocks the tree from a gene, or when the pawn already has the parent tree.
- **NFInnate** (on a weapon or apparel): seals, weaponSeal, armourSeal, rank. Seals the item always carries.
- **NFAuraFx** (on an ability or hediff): layers. Drawn aura layers.
- **KZEffect** (on an ability): kind (cone, strike, zone, shield, orb), element, tint, damageDef, damage, armorPenetration, extraDamageDef, extraDamage. Painted area and strike effects.
- **NFFactionInfo** (on a faction): group (main, minor, syndicate, venator, feudal), title, trees, headband, helmet, rank. How a faction fights and dresses, and whether it joins the war.
- **NFRitualItem** (on a ritual): kind, hediff, ticks, amount, radius, thing, curse, aug. What a ritual gives.

## Reporting a conflict
Send the NFRP_Patches.txt file, your mod list and the error from the log. If two mods patch the same method, the dev file shows which NFRP patch is there, so it is quick to see who needs to change.
