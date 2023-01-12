Fencer Module
=============

Fencer class
------------
.. autoclass:: fencer.Fencer

   .. automethod:: fencer.Fencer.__init__

   .. automethod:: fencer.Fencer.__str__

   .. automethod:: fencer.Fencer.short_str

   .. automethod:: fencer.Fencer.update_statistics

   .. automethod:: fencer.Fencer.win_percentage
   
   .. automethod:: fencer.Fencer.points_difference_int

   .. automethod:: fencer.Fencer.points_difference

   .. automethod:: fencer.Fencer.points_per_game

   .. automethod:: fencer.Fencer.points_against_per_game

   .. automethod:: fencer.Fencer.Wildcard


Wildcard class (subclass of Fencer)
-----------------------------------
.. autoclass:: fencer.Wildcard

   .. automethod:: fencer.Wildcard.__init__

   .. automethod:: fencer.Wildcard.update_statistics

   .. automethod:: fencer.Wildcard.points_against_per_game

   .. automethod:: fencer.Wildcard.points_per_game

   .. automethod:: fencer.Wildcard.points_difference

   .. automethod:: fencer.Wildcard.win_percentage


Stage class
-----------
.. autoclass:: fencer.Stage
   
   .. automethod:: fencer.Stage.__str__

   .. automethod:: fencer.Stage.next_stage