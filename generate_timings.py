import math
import os
import random
import sys

# PLAYER FUNCTIONS
#
# A Player Function is any function which takes a single argument consisting of
# the number of players, and returns a list of the player ids in the order they
# should play.  For example:
# [1, 2, 3, 4] says that player 1 should go first, followed by 2 then 3 then 4.
# [3, 2, 1] says that player 3 should go first, followed by 2 then 1.

# SINGLE_PLAYER always has a single player.
def SINGLE_PLAYER(player):
  def PlayerFunction(num_players):
    return [player]

# IN_ORDER is a pre-defined Player Function that just says that the players go
# in order.
def IN_ORDER(num_players):
  return [x for x in xrange(num_players)]

# REVERSE_ORDER is the reverse of IN_ORDER.
def REVERSE_ORDER(num_players):
  x = IN_ORDER(num_players)
  x.reverse()
  return x

# EVEN_PLAYERS selects only the even players, in increasing order like IN_ORDER.
def EVEN_PLAYERS(num_players):
  return [x for x in xrange(num_players) if x % 2 == 0]

# EVEN_PLAYERS selects only the odd players, in increasing order like IN_ORDER.
def ODD_PLAYERS(num_players):
  return [x for x in xrange(num_players) if x % 2 == 1]

# BOUNCE iterates IN_ORDER and then back again.  For example 1, 2, 3, 4, 3, 2.
def BOUNCE(num_players):
  return IN_ORDER(num_players) + REVERSE_ORDER(num_players)[1:-1]

# Returns the duration of a list of events.
def Duration(events):
  if len(events) == 0:
    return 0
  if len(events) == 1:
    return events[0].stop - events[0].start

  return events[-1].stop - events[0].start

# NOTE FUNCTIONS:
#
# A Note Function is a function which takes a player step number and a player
# number, and returns a list of notes.

# NOTE_LIST is a pre-defined Note Function which always returns the same list of
# notes regardless of the step number or player number.
def NOTE_LIST(notes):
  def ReturnNotes(step_number, player_number):
    return notes
  return ReturnNotes

REST = True

# A Note is anything which can yield a number of beats and whether or not it's a
# rest.
class Note:
  def GetBeats(self):
    return self.beats

  def IsRest(self):
    return self.is_rest

# A Dotted Note wraps another Note and increases its beats by 1.5 times.
class Dotted(Note):
  def __init__(self, note):
    self.note = note

  def GetBeats(self):
    return self.note.GetBeats() * 1.5

  def IsRest(self):
    return self.note.IsRest()

# A Tie takes any number of notes and concatenates them together.  You can't
# include rest notes inside a tie.
class Tie(Note):
  def __init__(self, *args):
    self.notes = args

    # Make sure there are no rest notes.
    for note in self.notes:
      assert not note.IsRest()

  def GetBeats(self):
    return sum([x.GetBeats() for x in self.notes])

  def IsRest(self):
    return False

# An Arbitrary Note lets you specify the number of beats directly.
class ArbitraryNote(Note):
  def __init__(self, beats, is_rest=False):
    self.beats = beats
    self.is_rest = is_rest

# The following are pre-defined commonly used note durations.
class Sixteenth(Note):
  def __init__(self, is_rest=False):
    self.beats = 0.25
    self.is_rest = is_rest

class TripletEighth(Note):
  def __init__(self, is_rest=False):
    self.beats = 1 / 3.0
    self.is_rest = is_rest

class Eighth(Note):
  def __init__(self, is_rest=False):
    self.beats = 0.5
    self.is_rest = is_rest

class TripletQuarter(Note):
  def __init__(self, is_rest=False):
    self.beats = 2 / 3.0
    self.is_rest = is_rest

class Quarter(Note):
  def __init__(self, is_rest=False):
    self.beats = 1
    self.is_rest = is_rest

class TripletHalf(Note):
  def __init__(self, is_rest=False):
    self.beats = 4 / 3.0
    self.is_rest = is_rest

class Half(Note):
  def __init__(self, is_rest=False):
    self.beats = 2
    self.is_rest = is_rest

class Whole(Note):
  def __init__(self, is_rest=False):
    self.beats = 4
    self.is_rest = is_rest

# TEMPO FUNCTIONS:
#
# Some pre-defined Tempo functions.  A tempo function is any function which
# accepts a time-stamp which is relative to the beginning of the start of a
# gesture, and returns a BPM.

# FIXED_TEMPO always returns the same BPM regardless of timestamp.
def FIXED_TEMPO(bpm):
  def ReturnTempo(global_start_time):
    return bpm
  return ReturnTempo

# TEMPO_RAMP ramps the tempo linearly from from_bpm to to_bpm over the course of
# duration seconds.
def TEMPO_RAMP(from_bpm, to_bpm, duration):
  def ReturnTempo(timestamp):
    if timestamp < 0:
      return from_bpm
    if timestamp > duration:
      return to_bpm

    frac = timestamp / float(duration)
    return from_bpm * (1.0 - frac) + to_bpm * frac
  return ReturnTempo

# SINE_TEMPO creates a tempo which alternates between low and high BPM in a
# sinusoidal manner.
def SINE_TEMPO(low, high):
  assert low < high

  def ReturnTempo(timestamp):
    return low + (high - low) * (1 + math.sin(timestamp)) / 2
  return ReturnTempo


# An Event is anything representing a player playing an instrument for a
# duration.
class Event:
  def __init__(self, player_num, instrument, start, stop):
    self.player_num = player_num
    self.instrument = instrument
    self.start = start
    self.stop = stop

  def __str__(self):
    return "%d(%s) %.2f -> %.2f" % (self.player_num, self.instrument,
        self.start, self.stop)

  def __repr__(self):
    return self.__str__()


class Gesture:
  def __init__(self):
    self.travel_function = IN_ORDER
    self.notes = None
    self.instrument = "UNKNOWN INSTRUMENT"
    self.time_between_players = self.GetTimeAfterPlayer

  # Returns a list of times.
  def GetNotes(self, player_number):
    return self.notes

  def GetInstrument(self):
    return self.instrument

  # Returns the time in between player X finishing and player X + 1 starting.
  def GetTimeAfterPlayer(self, player_num, previous_player_duration):
    return 0

  def Generate(self, num_players, steps, tempo_generator, start_time):
    # Grab our player order.
    player_order = self.travel_function(num_players)

    # Prepare our set of events.
    running_start = 0
    events = []

    for step in xrange(steps):
      # Figure out who the player is for this step.
      player = player_order[step % len(player_order)]

      # Get the notes for this player, and figure out how long they are.
      notes = self.notes(step, player)
      duration_for_player = 0
      for note in notes:
        beat_length = note.GetBeats()
        player_start = running_start
        tempo = 60.0 / tempo_generator(player_start)
        player_stop = player_start + tempo * beat_length
        running_start = player_stop
        duration_for_player += player_stop - player_start

        if note.IsRest():
          # We don't need to create events for rest notes.
          continue

        events.append(Event(player,
          self.instrument,
          start_time + player_start,
          start_time + player_stop))

      running_start += self.time_between_players(player,
          duration_for_player)

    return events


def HTMLHeader(out):
  out.write("""
<html>
<head>
<style>
div.span-mark {
  border: 1px black solid;
  position: absolute;
  opacity: 0.8;
  overflow: hidden;
  font-size: 8pt;
  line-height: 4px;
}
div.marker {
  position: absolute;
  background-color: black;
  z-index: -1;
}
div.cross-marker {
  position: absolute;
  background-color: #EEEEEE;
  z-index: -1;
}
div.timestamp {
  position: absolute;
  text-align: center;
  border: 1px solid black;
  padding: 2px;
}
div.players {
  position: fixed;
  bottom: 100;
  left: 100;
}
div.instrument {
  border: 1px black solid;
  width: 10px;
  height: 10px;
  float: left;
  background: white;
}
div.controls {
  position: fixed;
  bottom: 50;
}
#timeline-wrapper {
  position: relative;
}
html, body {
  margin: 0;
  padding: 0;
}
</style>
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
</head>
<body>
<div id="timeline-wrapper">
  """)

def WritePlayers(num_players, instruments, out):
  out.write("<div class='players'>")
  for pn in xrange(num_players):
    out.write("<div id='player-%d'>" % pn)
    for instrument in xrange(len(instruments)):
      out.write("  <div class='instrument' id='%s'></div>" % instrument)
    out.write("</div>")
  out.write("</div>")

def WriteControl(out, piece_length):
  out.write("""

</div>
<div class="controls">
<span id="top">&lt;&lt;</span> | <span id="play">Play</span> | <span

id="stop">Stop</span>
</div>

<script>
$("#top").click(function() {
  $("body").scrollLeft(0);
});
$("#play").click(function() {
  var instrumentColors = [
    "red", "blue", "green", "yellow", "cyan", "orange", "brown", "black",
  ];
  var eventsInOrder = []
  var spans = $(".span-mark");
  for (var i = 0; i < spans.length; i++) {
    var start = $(spans[i]).attr("start-ms");
    var stop = $(spans[i]).attr("stop-ms");

    var onInfo = {"player": $(spans[i]).attr("player"),
                  "instrument": Number($(spans[i]).attr("instrument")),
                  "action": "on"}
    var offInfo = {"player": $(spans[i]).attr("player"),
                   "instrument": Number($(spans[i]).attr("instrument")),
                   "action": "off"}

    eventsInOrder.push({"ts": start, "info": onInfo});
    eventsInOrder.push({"ts": Number(stop) - 20, "info": offInfo});
  }
  eventsInOrder.sort(function(a, b) { return a.ts- b.ts});

  var currentPosition = $("body").scrollLeft();
  var seconds = """ + str(piece_length) + """;
  var pixelsPerSecond = 70;
  var eventIndex = 0;
  $("body").animate({scrollLeft: currentPosition + (pixelsPerSecond * seconds)},
    {
      duration: 1000 * seconds,
      easing: "linear",
      step: function(left) {
        var ts_ms = (left / pixelsPerSecond) * 1000;
        var newEventIndex = eventIndex;
        for (var i = eventIndex; i < eventsInOrder.length; i++) {
          if (eventsInOrder[i].ts < ts_ms) {
            // Execute it!
            var event = eventsInOrder[i];
            var color = "white";
            if (event.info.action === "on") {
              color = instrumentColors[event.info.instrument]
            }

            var player = $("#player-" + event.info.player);
            var instrument = player.children("#" + event.info.instrument);
            instrument.css("background", color);
            newEventIndex = i + 1;
          } else {
            break;
          }
        }

        eventIndex = newEventIndex;
      }
    });
});
$("#stop").click(function() {
  $("body").stop();
});
</script>

</body>
</html>
""")

EDGE = 70

colors = []
for i in xrange(30):
  colors.append((random.randrange(255), random.randrange(255),
      random.randrange(255)))

def Events2HTML(out, instruments, events):
  for event in events:
    div = """
<div class="span-mark"
     start-ms="%d"
     stop-ms="%d"
     player="%d"
     instrument="%d"
     style="top: %dpx; left:%dpx; width: %dpx; height: %dpx; background-color: #%02x%02x%02x;">
     <p>%s</p>
</div> """

    filled_div = div % (
        event.start * 1000.0,
        event.stop* 1000.0,
        event.player_num,
        instruments.index(event.instrument),
        event.player_num * (EDGE/2),
        event.start * EDGE,
        (event.stop - event.start) * EDGE - 1,
        EDGE / 2 - 1,
        colors[event.player_num][0],
        colors[event.player_num][1],
        colors[event.player_num][2],
        event.instrument)

    out.write(filled_div)

def TimeGrid(out, max_seconds):
  marker_height = EDGE * 6

  for player in xrange(1, NUM_PLAYERS + 1):
    div = """
<div class="cross-marker" style="top: %d; width: %d; height: 1px;"></div>
""" % (player * (EDGE/2), max_seconds * EDGE)
    out.write(div)

  for i in xrange(max_seconds):
    div = """
<div class="marker" style="top: 0; left: %dpx; width: 1px; height: %dpx;"></div>
""" % (i * EDGE, marker_height)
    out.write(div)

    div = """
<div class="timestamp" style=" top: %d; left: %d;">%s</div>
""" % (marker_height, i * EDGE, "%d:%02d" % (i/60, i%60))
    out.write(div)

def START_GESTURE(gesture, player_steps, start_time, tempo):
  global visualization_file
  global all_instruments
  global piece_length

  if not gesture.instrument in all_instruments:
    all_instruments.append(gesture.instrument)

  # Generate the events.
  events = gesture.Generate(
      NUM_PLAYERS,
      player_steps,
      tempo,
      start_time)

  # Write them to the HTML file.
  Events2HTML(visualization_file, all_instruments, events)

  # Update the duration of the piece.
  for e in events:
    piece_length = int(max(piece_length, math.ceil(e.stop)))

if __name__ == "__main__":
  # Check that the args make sense.
  if len(sys.argv) != 2:
    print "Usage: %s <input file>" % sys.argv[0]
    sys.exit(1)

  if not os.path.isfile(sys.argv[1]):
    print "Unknown file: %s" % sys.argv[1]
    sys.exit(1)

  # Prepare for executing the program.
  visualization_file = file("vis.html", "w")
  HTMLHeader(visualization_file)
  piece_length = 0
  all_instruments = []

  execfile(sys.argv[1])

  TimeGrid(visualization_file, piece_length + 60)
  WriteControl(visualization_file, piece_length)
  WritePlayers(NUM_PLAYERS, all_instruments, visualization_file)
