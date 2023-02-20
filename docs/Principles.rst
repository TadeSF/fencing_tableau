==================================
Main Principles and Program Desing
==================================
The purpose of this Web-Application is to assist in the running of small and informal fencing tournaments at a club level.
It will aim to provide the option of having one or multipe preliminary rounds, followed by a direct elimination, with the additional option of having placement matches or a repechage.
It aims to provide the possibility both of a seeded starting list and of random seeding.

The backend of the Web-Application is written in Python, and the frontend is written in HTML5, Javascript and SCSS. It is run on a public server, but can alternativly be run locally and hosted inside a local network.

The Web-Application is designed to have multiple usage and access levels, providing the tournament maneger/organiser (here called "master") with the ability to create and manage tournaments, the referees with the ability to organise their respective piste and the participants (fencers) with the ability to follow the tournament proceedings and to view their results and statistics.

For the master, the Web-Application is designed to be used on a computer. The referees are expected to use a tablet or a smartphone, while the participants are expected to use a smartphone.

*************************
Combinatorics and Seeding
*************************
This section seeks to outline the logical and combinatoric foundations of the various rounds in a fencing competition.

The goal of any competition is to accurately determine the relative rank of all competitors (usually with a particular emphasis on the first ranks). It should do this in as efficient and timely manner as possible. The primary trade-off is generally between accuracy and efficiency, the various modes available representing different choices regarding this trade-off, within the bounds set by the starting field and local conditions.

Seeding
=======

It is generlly desireable that some form of seeding takes place.This is to ensure, that the tournament remains fair and interesting throughout (i.e. that the groups in the preliminary rounds are balanced and that the final has the highest probability of matching the two best fencers in the competition against each other).

The basis for seeding can be international, national or regional rankings, so far as they are available. If these are used, unranked fencers are randomised and appended to the ranked list. For smaller tournaments (e.g. within a club), it is usually preferable to make an informal ranking, roughly based on the experience of the organiser. Especially in smaller tournaments unballanced groups can seriously skew the end results. For regular events, it is sometimes customary for the winner (and runner-up) of the previous tournament to be given the top seeds, irrespective of their current rating.

Unseeded
========
If there is no prior ranking or the majority of fencers are unranked, the entire field should be randomised. This is often the case for large informal tournaments (e.g. for students). If there is sufficient time, it is advisable to conduct a second preliminary round in these cases.

Preliminary Round
=================
There are to methods of distributiong the fencers within the groups: Either consecutively or using a "snake draft". In the first case, for n groups, the first n fencers are assigned consecutively to the groups 1 to n; the fencers from n+1 to 2n are again assigned consecutively to groups 1 to n and so forth. In the second case, for n groups, the first n fencers are assigned consecutively to the groups 1 to n, the fencers from n+1 to 2n are then assigned to the groups in reverse order; with each run through the groups, the order of assignement is reversed.

The benefit of the first method is that the first groups are invariably the larger ones. It is, however, significantly less fair, the first group being comparatively stronger on average than the subsequent groups. When there is a large number of groups, the divergence between the first and last group can be considerable.

Second Preliminary Round (without elimination)
==============================================
The primary purpose of a second preliminary round without eliminations is to compensate the absence of rankings. The results of the first round are used to seed the second round. This makes the elimination round fairer and more representative and can eliminate improbable but possible occurences that are otherwise capable of significantly skewing the final results. Otherwise this round is conducted in the same manner as the first. The ranking for the elimination round is calculated by combining the results of both preliminary rounds. This is done either by averaging the first index and summing the second index, or, for the first index summing the constituent elements and recalculating the index (the latter avoids rounding errors). In some cases it may be desireable to weight the rounds towards the second round (although this is mostly unnecessary and fairly difficult to implement).

Second Preliminary Round (with elimination)
===========================================
The elimination of fencers in the preliminary round is unusual for most tournaments. In some official tournaments, however, only 32 or 16 fencers progress to the direct elimination rounds. There is, however, a limit placed on the number of fencers that can be eliminated in one preliminary round. If the number of fencers in the competition exceeds this number, further preliminary rounds are held until the desired number remain. (The rules of the DFB stipulate that only 1/3 of fencers can be eliminated per preliminary round.)

Groups in General
=================
The order of matches within the groups should aim to distribute them fairly and evenly. When only one piste is used per group, each fencer should have a break of at least one match between matches. In larger groups the length of breaks should also not be too long and the number of longer breaks should be evenly distributed between all fencers in the group. It is also preferable to evenly distribute the amount of times each fencer occupies each side of the piste (local conditions can give an edge to the person occupying a particular side). It was formerly common practice to place left-handed fencers, when facing right-handed fencers, on the left side of the piste. This is, however, no longer officially required.

Elimination Rounds (128-8)
==========================
The elimination round usually consists of the next highest power of two to the number of participants, the fencer ranked first is matched with the 2^xth fencer, the 2nd with the 2^x-1 and so forth. If the number of fencers is less than 2^x, the highest ranked fencers get a bye for that round. (I.e. if there are 2^x-n fencers, the first n fencers get a bye and the n+1th fencer faces the last placed fencer.) In the subsequent rounds byes only have to be given if one or more fencers leave the competition due to injury or disqualification. (Disqualified fencers are entirely eliminated from the standings -- including all matches they fought up to the point of disqualification --, injured fencers usually retain the rank they had before their injury.)

In order to have a certain degree of predictability, the position of the higher seeded fencer alternates in the elimination round, the first fencing on the left, the second on the right and so forth. Exceptions can be made when left-handed fencers face right-handed fencers. In order to simplify the graphical representation of the elimination table, the fencers can be ordered as follows (beginning at the top): 1, n, n/2+1, n/2, n/4+1, 3n/4, 3n/4+1, n/4, n/8+1, 7n/8, 5n/8+1, 3n/8,3n/8+1, 5n/8, 7n/8+1, n/8...

This serves the purpose that, if the preliminary rounds were accurate, the best two fencers meet in the final and tension builds gradually over the course of the elimination rounds.

If the lower ranked fencer wins an elimination match, they usually assume the defeated fencer's position in the tournament tree. They do not, however, assume their rank in the interim or final ranking. (I.e. if the 1st ranked fencer is defeated by the 32nd in the round of 32 (assuming that in all other matches the higher ranked fencer wins), the victorious fencer assumes the 16th rank, whereas the other fencer is eliminated with a final rank of 17th. If the lower ranked fencer wins in multiple matches, the relative rank from the previous round is retained. If all lower ranked fencers win in the quarter-finals, the interim ranking would be: 5,6,7,8,1,2,3,4.) This is only relevant if there are no placement matches.

Finals
======
Even if there are no placement matches in general, the two defeated semi-finalists will often fight a bronze-medal match. If this is not the case, they are both awarded the third place, irrespective of their interim ranks.

Placement Matches
=================
If there are no placement matches, the fencers eliminated after the first round are ranked solely on the basis of their relative performance in the preliminary round(s). It also means that there is a significant difference in the number of matches fought by those who are eliminated in the first elimination round and those who reach the final. If there is a sufficient capacity of pistes, it can be desireable for all fencers to have the opportunity to have a large number of matches.

Placement matches are held between the losers of the preceding elimination round. In effect they mirror the elimination round. (E.g. after the round of 32, the 17th faces the 32nd, the 25th the 24th and so on. This is repeated after each round. The fencers do not have multiple elimination matches. If one or more higher ranked fencers lose their elimination matches in a given round, there are two possibilities: Either they assume the placement of the fencer that defeated them, or they are ranked above the highest lower ranked fencer to lose their elimination bout. The former is significantly easier to implement, the latter is somewhat fairer for all fencers.

Repechage
=========
A repecharge is usually only used for very small tournaments (16 fencers or fewer). It offers the possibility for fencers to come back into the main table after they have been eliminated in the first round. Effectively a fencer is only eliminated after they have lost their second match. A normal round of 16 is held. The losers (A) of this round then face eachother (16-9, 12-13, 14-11, 10-15), as do the victors (B) (in the normal order of a round of 8). The victors of the former matches then face the losers of the latter matches (C). The victors of (C) then face the victors of (B) in the quater finals. The rest of the elimination (QF & F) procedes as normal.

It is, in theory, possible to extend this mode to more fencers or to cover more rounds. It is, however, rarely practicable to use this mode more extensively as it requires significantly more bouts per round of elimination, although the aim of reducing randomness is laudable. For a relatively small number of fencers it is, perhaps, preferable to a second preliminary round, as a certain degree of excitement is maintained in comparisson.

Marathon
========
Every fencer faces every other fencer once. When sufficient time is available, this is the most accurate and rewarding option. It does, however, involve signifficantly more bouts for each fencer, particularly the lower rated ones (31 bouts for a field of 32 fencers, as compared to 6-13 bouts for a preliminary round and eliminations). It thus requires a large amount of time and endurance -- hence the name!

It is usually diffcult to organise ad hoc at a large scale. (This is where this programme may be a significant help, adjusting to bouts of differnt lengths and assigning fencers to pistes at short notice, while ensuring sufficient breaks for each fencer.) The ususal and more manageable approach is to group fencers into groups of 5-7 fencers and then have these groups face each other, thus gradually completing various quadrants of a giant tableau. At some point the fencers within each group must, of course, face eachother.

(Swiss System)
==============
This is a mode never used in fencing tournaments.

Mixed Competitions
==================
If the competition is mixed, a separate final rating by gender may be provided, particularly of the highest ranked woman, so that they can be individually honoured. This is usually only done for the final rankings and not at any intermediate stage.


*******************
Maximal Aspirations
*******************
Some thoughts and considerations on what options, functions and features a fencing programme could have. The purpose is not to provide an overview of future features, but rather to delineate the space of possibilities within which this programme exists.

Since this Section is more an overview and source of inspiration for the developers, it will be in German and is probably not updated regulary.

Turnierprogramm: 4 Pfeiler
==========================
1. Wettkampf-Management (Laptop): Registration von Teilnehmenden (Name, Verein, Seed; ggf. Geschlecht, Hand), Erstellung von Tableaux und Turnierbäumen (inklusive Druckvorlagen), Eingabe von Ergebnissen, Berechnung der Rangliste und Siegenden, Ausgabe der Resultate (inklusive Druckvorlagen).
2. Gruppen- und Match-Management (Mobil): Client für Darstellung des Gruppenspezifischen Tableaus (Selektion durch z.B. QR-Code), automatische Vervollständigung des Tableaus, Abgabe der individuellen Ergebnisse an den Server/das Wettkampf-Management, Bestätigung der Richtigkeit der Ergebnisse durch Fechtende (nach gesamter Runde), ggf. Korrektur der Ergebnisse, Idealerweise: Aufruffunktion für Runden und einzelne Gefechte.
3. Gefecht-Management (Mobil): Automatische Übernahme der Wettkampfvorgaben, Zeitabnahme (ggf. mit Pause), Punkterfassung, Karten (ggf. mit Begründung), Trennung von Karten und P-Karten (evtl. Passivitätstimer), Bestätigung der Richtigkeit durch Fechtende (nach dem einzelnen Gefecht), Übertragung des Ergebnisses ins lokale Tableau (evtl. auch ans zentrale Wettkampf-Management); Idealerweise auch Anbindung an die Meldeanlage.
4. Ergebnisdarstellung (Mobil, Online, Bildschirm, Papier): Möglichst aktuelle Darstellung sämtlicher Resultate (ggf. vorläufig), in möglichst vielen Medien, strikte Trennung vom bearbeitbarem Teil, Slideshow-Funktion für lokale Bildschirme, Druckvorlagen (wie bereits in 1. erwähnt).

Allgemeine Features/Optionen
============================
- Waffen (Degen/Florett,Säbel).
- Einzel/Team.
- Damen/Herren.
- Altersklassen.
- Rollstuhl/Laufen.
- (Separate Wertung gemäß obiger Faktoren).
- 4-512 Teilnehmende (prinzipiell hohe Erweiterbarkeit nach oben). (128 ist vermutlich der Standard.)
- Verschiedene Turniermodi (ein/zwei/keine Vorrunde, mit/ohne Setzung, mit/ohne Hoffnungslauf, ABC…-Finals).
- Anzahl der vorhandenen Bahnen.
- Variation der Wettkampf-Parameter (Zeit & Punkte der individuellen Runden/Gefechte).
- Disqualifikation & andere Disziplinarmaßnahmen.
- Idealerweise: Ligasystem & ewige Rangliste (zeitübergreifend). Funktion für größeren Marathon (128 mit kleinen Gruppen gegeneinander).
- Ranglisten-Server (regional, national, international).
- Ungewöhnliche Modi (Waffenmischungen, Nichtbinäre Gefechte).
- Offline-Modus (mit lokaler, (halb-)analoger Datenübertragung).


*******************
Official Guidelines
*******************
Here follows a roundup of the official rules governing the format of fencing competitions as promulgated by the governing bodies Federation International d'Escrime and Deutscher Fechterbund. As this programme is primarily intended for informal competitions, these rules are not considered to be binding.

The general rules from the FIE concerning individual competitons are contained in this document_ (o.66 ff.).
.. _document: https://static.fie.org/uploads/29/147895-Organisation%20rules%20ang.pdf