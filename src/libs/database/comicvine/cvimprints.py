# encoding: utf-8

'''
This module is used to find imprint names for publishers in the ComicVine 
database.  

Since ComicVine doesn't directly store imprint information, we are forced to 
maintain a internal tables of known imprints and their publishers in order to
do this.

If you run this module, it will query the ComicVine database and report the
discrepancies between the publishers in ComicVine, and the ones in our
internal tables (i.e. when a new publisher appears, you can easily find out 
about it and add it to the internal tables.) 

@author: Cory Banack
'''

import clr
import log
import re
from utils import sstr

clr.AddReference('System')
from System import Text
from System.IO import StreamReader, StringWriter

clr.AddReference('System.Net')
from System.Net import WebException, WebRequest


clr.AddReference('System.Web')
from System.Web import HttpUtility

# =============================================================================
def find_parent_publisher(imprint_s):
   '''
   This method takes a publisher string that might be an imprint of another 
   publisher.  If it is an imprint, the method returns a different publisher 
   string representing the parent publisher for that imprint.  If it is not 
   an imprint, this method returns the string that was passed in.
   
   Both the passed in and returned strings for these methods should EXACTLY
   match their corresponding values in the ComicVine database (i.e. case, 
   punctation, etc.)
   ''' 
   imprint_s = imprint_s.strip() # because the tables below are stripped, too
   parent_s = imprint_s
   if imprint_s in __imprint_map:
      parent_s = __imprint_map[imprint_s]
   return parent_s


# the publishers that we know about that have at least one imprint
__MARVEL = "Marvel"
__DC = "DC Comics"
__DARKHORSE = "Dark Horse Comics"
__MALIBU = "Malibu"
__AMRYL =  "Amryl Entertainment"
__AVATAR = "Avatar Press"
__WIZARD = "Wizard"
__TOKYOPOP = "Tokyopop"
__DYNAMITE = "Dynamite Entertainment"
__IMAGE = "Image"
__HEROIC = "Heroic Publishing"
__PENGUIN = "Penguin Group"
__HAKUSENSHA = "Hakusensha"
__APE = "Ape Entertainment"
__NBM = "Nbm"
__RADIO = "Radio Comix"
__SLG = "Slg Publishing"
__TOKUMA = "Tokuma Shoten"

# the mapping of imprint names to their parent publisher names
__imprint_map = {
   "2000AD": __DC,
   "Adventure": __MALIBU,
   "America's Best Comics": __DC, # originally image
   "Wildstorm": __DC,
   "Antimatter": __AMRYL,
   "Apparat": __AVATAR,
   "Black Bull": __WIZARD,
   "Blu Manga": __TOKYOPOP,
   "Chaos! Comics": __DYNAMITE,
   "Cliffhanger": __DC,
   "CMX": __DC,
   "Dark Horse Manga": __DARKHORSE,
   "Desperado Publishing": __IMAGE,
   "Epic": __MARVEL, 
   "Focus": __DC, 
   "Helix": __DC,
   "Hero Comics": __HEROIC,
   "Homage comics": __DC, # i.e. wildstorm
   "Hudson Street Press": __PENGUIN,
   "Icon Comics": __MARVEL,
   "Impact": __DC,
   "Jets Comics": __HAKUSENSHA,
   "KiZoic": __APE,
   "Marvel Digital Comics Unlimited" : __MARVEL,
   "Marvel Knights": __MARVEL,
   "Marvel Music": __MARVEL,
   "Max": __MARVEL,
   "Milestone": __DC,
   "Minx": __DC,
   "Papercutz": __NBM,
   "Paradox Press": __DC,
   "Piranha Press": __DC,
   "Razorline": __MARVEL,
   "ShadowLine": __IMAGE,
   "Sin Factory Comix" : __RADIO,
   "Slave Labor": __SLG,
   "Soleil": __MARVEL,
   "Tangent Comics": __DC,
   "Tokuma Comics": __TOKUMA,
   "Ultraverse": __MALIBU,
   "Vertigo": __DC,
   "Zuda Comics": __DC,
}

# a set of all non-imprint publishers in the comic vine database
# (used only for the imprint search script below)
__other_publishers = frozenset([
   __MARVEL,
   __DC, 
   __DARKHORSE,
   __MALIBU,
   __AMRYL,
   __AVATAR,
   __WIZARD,
   __TOKYOPOP,
   __DYNAMITE,
   __IMAGE,
   __HEROIC,
   __PENGUIN,
   __HAKUSENSHA,
   __APE,
   __NBM,
   __RADIO,
   __SLG,
   __TOKUMA,
   "01Comics.com",
   "12 Gates Productions",
   "12-Gauge Comics",
   "1st Amendment Publishing",
   "2-D Graphics",
   "20000 Leagues",
   "215 INK",
   "21st Century Sandshark Studios",
   "24 Hour Cynic",
   "2Werk",
   "3 Finger Prints",
   "3-D Zone",
   "3-M",
   "360ep",
   "3DO Comics",
   "3H Productions",
   "3ntini Editore",
   "4 Winds",
   "5th Panel Comics",
   "801 Media",
   "803 Studios",
   "88 MPH",
   "8th Day Entertainment",
   "9th Circle Studios",
   "A",
   "A D Vision",
   "A Division Of Malibu Graphics",
   "A List Comics",
   "A Silent Comics Inc",
   "A Wave Blue World",
   "A-Plus",
   "A.M. Works",
   "A.R.C.",
   "A10 Comics",
   "AAA Milwaukee",
   "AAA Pop",
   "AC",
   "ADV Manga",
   "AKA Comics",
   "ANIA",
   "APComics",
   "AS Film Inform",
   "Aardvark",
   "Aardwolf Productions",
   "Aazurn",
   "Abaculus",
   "Abacus Press",
   "Abbeville Press",
   "Aberration Press",
   "Abiogenesis Press",
   "Ablaze Media",
   "Abnormal Fun",
   "About Comics",
   "Abril",
   "Absence Of Ink",
   "Absolute Blue Graphics",
   "Absolute Tyrant",
   "Abstract Studio",
   "Ac Collector Classics",
   "Academy Comics Ltd",
   "Acclaim",
   "Ace Comics",
   "Ace Magazines",
   "Ace Publications Inc",
   "Acetylene",
   "Acg",
   "Acid Rain Studios",
   "Acme",
   "Across The Pond Studios",
   "Action Folksinger",
   "Action Planet Comics",
   "Active Images",
   "Active Synapse",
   "Adhesive Comics",
   "Adhouse Books",
   "Adversary Comix",
   "Aeon",
   "Aerosol Press",
   "After Hours Press",
   "Afterburn Comics",
   "Aftershock Comics",
   "Age Of Heroes",
   "AiT/Planet Lar",
   "Airbrush",
   "Aircel Publishing",
   "Airship Entertainment",
   "Aja Blu Comix",
   "Ajax",
   "Ajax-Farrell",
   "Akita Shoten",
   "Al Fago Magazines",
   "Alamat Comics",
   "Albert Bonniers F",
   "Albin Michel",
   "Alchemy Studios",
   "Alchemy Texts",
   "Alfabeta",
   "Alias Enterprises",
   "Aliwan Comics",
   "All Thumbs Press",
   "All-Negro Comics",
   "Allers",
   "Allers Forlag",
   "Allied Comics",
   "Almighty Publishing",
   "Alpha Productions",
   "Alpha/Streck Enterprises",
   "Alpine Underground",
   "Alterna Comics",
   "Alternative Press",
   "Alvglans",
   "Amalgam Comics", # this is marvel AND dc? what to do?
   "Amalgamated Press",
   "Amazing Aaron Productions",
   "Amazing Comics",
   "Amazing Creations Ink",
   "Ambrosia Publishing",
   "American Cancer Society",
   "American Comics Group",
   "American Friends Service Committee",
   "American Mule",
   "American Red Cross",
   "American Visuals Corporation",
   "Americanime",
   "Americomics",
   "Amerotica",
   "Anarchy Studios",
   "Andrews And Mcmeel",
   "Angel Entertainment",
   "Angel Gate Press",
   "Angry Viking Press",
   "Anime Works",
   "Another Rainbow",
   "Antarctic Press",
   "Anti-Ballistic Pixelations",
   "Anubis Press",
   "Anvil",
   "Apocalypse",
   "Apple",
   "Application Security, Inc.",
   "Approbation Comics",
   "Aragon",
   "Arcade Comics",
   "Arcana Studio",
   "Archaia Studios Press",
   "Archangel Studios",
   "Archie",
   "Archie Adventure Series",
   "Ardden Entertainment",
   "Argo Publications",
   "Aria Press",
   "Aries Publications",
   "Arleigh",
   "Armada",
   "Armageddon Press Inc.",
   "Arnoldo Mondadori Editore",
   "Arrache Coeur",
   "Arrow",
   "Arsenic Lullaby Publishing",
   "Askild",
   "Aspen MLT",
   "Asplunds",
   "Astonish Comics",
   "Astorina",
   "Astronaut Ink",
   "Asuka Comics",
   "Asylum Press",
   "Atari",
   "Atlantic F",
   "Atlantis Studios",
   "Atlas",
   "Atlas Comics",
   "Atomeka Press",
   "Atomic Basement",
   "August House",
   "Austintations",
   "Avalon Communications",
   "Aviation Comics",
   "Avon",
   "Awesome",
   "Azteca Productions",
   "B",
   "B & H Publishing Group",
   "B&D Pleasures",
   "BBC Books",
   "BBC Magazines",
   "BC",
   "BKR Comics",
   "BSV - Williams",
   "Baby Tattoo Books",
   "Bad Dog Books",
   "Bad Habit Books",
   "Bad Karma Productions",
   "Bad Press Ltd",
   "Badroach Publications",
   "Bagheera",
   "Bailey Publishing Co",
   "Bakh",
   "Bald Guy Studios",
   "Baldini Castoldi Dalai Editore",
   "Ball Publishing",
   "Ballantine Books",
   "Bam",
   "Banana Tales Press",
   "Bandai Entertainment",
   "Bang! Entertainment",
   "Bantam Books",
   "Barbour Christian Comics",
   "Basement Comics",
   "Bastei Verlag",
   "Battlebooks Incorporated",
   "Baychild Productions",
   "Beanworld Press",
   "Beckett",
   "Belif",
   "Bell Features",
   "Berghs",
   "Berkley Books",
   "Berserker Comics",
   "Best Destiny",
   "Best Friends Publication",
   "Beta 3",
   "Betel",
   "Beyond Time Comic",
   "Big Balloon",
   "Big Bang Comics",
   "Big City Comics",
   "Big Dog Ink",
   "Big Head Press",
   "Big Shot Comics",
   "Big Umbrella",
   "Bioroid Studios",
   "Bishop Press",
   "Black Boar Press",
   "Black Cat Comics",
   "Black Coat Comics",
   "Black Diamond Effect Inc.",
   "Black Eye",
   "Black Library",
   "Black Rock Design",
   "Black ball Comics",
   "Blackline Studios",
   "Blacklist Studios",
   "Blackmore",
   "Blackout",
   "Blackthorne",
   "Bladkompaniet As",
   "Blind Ferret",
   "Blind Wolf",
   "Bliss on Tap Publishing",
   "Bloodfire Studios",
   "Bloody Mary Comics",
   "Blue Comet Press",
   "Blue King Studios",
   "Bluewater Productions",
   "Bob Ross",
   "Bodog",
   "Boemerang",
   "Bokf",
   "Bokfabriken",
   "Bokomotiv",
   "Bompiani",
   "Bones",
   "Boneyard Press",
   "Bongo",
   "Bonnier Carlsen",
   "Bonniers Juniorf",
   "Boom! Studios",
   "Boundless Comics",
   "Brain Scan Studios",
   "Brainstorm",
   "Brave New Words",
   "Brett's Comic Pile Publishing",
   "Brick Computer Science Institute",
   "Broadsword Comics",
   "Broadway",
   "Broken Halos",
   "Broken Tree Comics",
   "Broken Voice Comics",
   "Brown Shoe Company",
   "Bruce Hershenson",
   "Bubblehead Publishing",
   "Budget Books",
   "Buffalo Books",
   "Bulletproof Comics",
   "Burlyman Entertainment",
   "Buymetoys.com",
   "C.A.M. Press",
   "C.C.A.S. Publication",
   "C.M.I. Corporativo Mexicano de Impresión",
   "CARNIVAL COMICS",
   "CBG",
   "CEA Casa Editrice Astoria",
   "CFW Enterprises",
   "Cackling Imp Press",
   "Cafe Digital",
   "Cahaba Producttions",
   "Caliber Comics",
   "California Comics",
   "Cambridge House Publishers",
   "Candle Light Press",
   "Candlewick Press",
   "Canew Ideas",
   "Capcom",
   "Capital Comics",
   "Capitol Stories",
   "Capstone Press",
   "Captain Clockwork",
   "Caption Comics",
   "Carabosse Comics",
   "Carbon-Based Comics",
   "Carlsen Comics",
   "Carlton Publishing",
   "Carnal Comics",
   "Carnopolis",
   "Carol Ediciones S.A. de C.V.",
   "Cartoon Art",
   "Cartoon Books",
   "Casa Editrice Dardo",
   "Casa Editrice Universo",
   "Casterman",
   "Castle Rain",
   "Catalan Communications",
   "Catastrophic Comics",
   "Catwild Publications",
   "Celebrity",
   "Cellar Door Publishing",
   "Centaur",
   "Central Park Media",
   "Century Publications",
   "Cepim",
   "Cge From",
   "Channel M",
   "Chanting Monks Studios",
   "Chaotic Unicorn Press",
   "Charlton",
   "Checker Book Publishing Group",
   "Cherry",
   "Cherry Comics",
   "Chicago Mail Order Comics",
   "Chick Publications",
   "Children",
   "Chronicle Books",
   "Chuang Yi",
   "Cinebooks",
   "Circle Media",
   "Cirkelf",
   "Claypool Comics",
   "Club 408 Graphics",
   "Coffin Comics",
   "Colburn Comics",
   "Colour Comics Pty Ltd",
   "Columbia Comics",
   "Com.X",
   "Comely Comix",
   "Comic Art",
   "Comic Book Legal Defense Fund",
   "Comic Legends Legal Defense Fund",
   "Comic Media",
   "Comic Shop News Inc.",
   "Comico",
   "Comics Interview",
   "Comics Unlimited Inc.",
   "Comicsonair Publications",
   "Commercial Comics",
   "Commercial Signs Of Canada",
   "Committed Comics",
   "Company & Sons",
   "Comunicaciones Graficas Comgraf",
   "Condor Verlag",
   "Coniglio Editore",
   "Conquest Press",
   "Continuity",
   "Continum",
   "Conundrum Press",
   "Corgi",
   "Corriere Della Sera",
   "Crack",
   "Cracked Pepper Productions",
   "Craf Publishers",
   "CrankLeft",
   "Creative Impulse Publishing",
   "Creative One",
   "Creators Edge Press",
   "Creston Publishing Corporation",
   "Critical Mass",
   "Cross Plains Comics",
   "Cross Publications",
   "Crossgen",
   "Crown Publishers",
   "Croydon Publishing",
   "Crusade",
   "Crush Dice Comics Company",
   "Cry For Dawn Productions",
   "Cryptic Press",
   "Crystal Comics",
   "Ctrl Alt Del",
   "Cult Press",
   "Cupples & Leon",
   "Cyberosia Publishing",
   "Cyclone Comics",
   "D. S. Publishing",
   "D.C. Thomson & Co.",
   "DK Publishing",
   "DQU COMICS",
   "DWAP Productions",
   "Dab Enterprises",
   "Dabel Brothers Productions",
   "Dagens Nyheters F",
   "Dagger Enterprises",
   "Daim Press",
   "Dakuwaka Productions",
   "Dancing Elephant Press",
   "Danity Kane Comics",
   "Dare Comics",
   "Dargaud",
   "Dark Elf Designs",
   "Dark Fantasy Production",
   "Dark Ocean Studios",
   "Darkchylde Entertainment",
   "Darkmatter",
   "David Mckay",
   "David Miller Studios",
   "Dead Dog",
   "Dead Numbat Productions",
   "DeadBox Art Studio",
   "Deadline Publications Ltd.",
   "Def Con Comics",
   "Defiant",
   "Del Rey",
   "Dell",
   "Delta Verlag",
   "Deluxe",
   "Deluxe Comics",
   "Dengeki",
   "Dennis F",
   "Der Freibeuter",
   "Determined Productions, Inc.",
   "Devil's Due",
   'Dial "C" for Comics',
   "DigiCube",
   "Digital Manga Distribution",
   "Digital Webbing",
   "Dimension Graphics",
   "Dimestore Productions",
   "Dino Comics",
   "Disney",
   "Diva Graphix",
   "Do Gooder Press",
   "Dobry Komiks",
   "Dolmen Publishing",
   "Dork Storm",
   "Double A Comics",
   "Double Edge Publications",
   "Dover Publications",
   "Dr Master Productions",
   "DrMaster Publications Inc.",
   "Dragon Candy Productions",
   "Dragon Comics",
   "Dragon Lady Press",
   "Dramenon Studios",
   "Drawn",
   "Drawn & Quarterly",
   "Dreamwave Productions",
   "Drumfish Productions",
   "Dupuis",
   "Dynamic Forces",
   "Dynamite",
   "E",
   "Eagle Comics",
   "Eastern Color",
   "Eastern Comics",
   "Ec",
   "Echo 3 Worldwide",
   "Eclectic Comix",
   "Eclipse",
   "Eddie Campbell Comics",
   "Eden",
   "Edgewater Comics",
   "Ediciones B",
   "Ediciones José G. Cruz",
   "Ediciones La Cúpula S.L.",
   "Ediciones Latinoamericanas",
   "Ediciones de la Flor",
   "Edifumetto",
   "Ediperiodici",
   "Edition C",
   "Editions First - Gründ - Dragon d'Or",
   "Éditions Glénat",
   "Editions La Joie de Lire",
   "Editor",
   "Editora Trama",
   "Editora Vord",
   "Editorial Alfaguara",
   "Editorial Ejea",
   "Editorial Greco (Grupo Editorial Colombiano)",
   "Editorial Icavi Ltda.",
   "Editorial Juventud",
   "Editorial Manuel del Valle",
   "Editorial Novaro",
   "Editorial OEPISA",
   "Editorial Rodriguez",
   "Editorial Televisa",
   "Editorial Toukan",
   "Editorial Tucuman",
   "Editoriale Corno",
   "Editoriale Mercury",
   "Editormex Mexicana",
   "Editrice Cenisio",
   "Editrice Puntozero",
   "Edizioni Alpe",
   "Edizioni Araldo",
   "Edizioni Audace",
   "Edizioni BD",
   "Edizioni San Paolo",
   "Edizioni Star Comics",
   "Edizioni d’Arte “Lo Scarabeo”",
   "Educomics",
   "Edwin Aprill",
   "Eerie Publications",
   "Egmont",
   "Ehapa Verlag",
   "El Capitan",
   "El Mundo",
   "Electric Spaghetti Comics",
   "Elevenstone Studios",
   "Elite Comics",
   "Elvifrance",
   "Empresa Editora Zig Zag S.A.",
   "Endless Horizons Entertainment",
   "Enemy Transmission",
   "Enigma Comics",
   "Enterbrain",
   "Entity",
   "Entity Comics",
   "Enwill Associates",
   "Epix",
   "Eros Comix",
   "Esteem Comics",
   "Etc",
   "Eternal",
   "Eternity",
   "Eura Editoriale",
   "Eurotica",
   "Event Comics",
   "Everyman Studios",
   "Evil Twin Comics",
   "Evolution Comics",
   "Excellent Publications",
   "Exploding Albatross Funnybooks",
   "Express",
   "Extreme",
   "F",
   "FC9",
   "Fabel",
   "Factoid Books",
   "False Idol Studios",
   "Famous Funnies",
   "Fandom House",
   "Fangoria",
   "Fantaco",
   "Fantaco Enterprises",
   "Fantagor Press",
   "Fantagraphics",
   "Farrar, Straus, and Giroux",
   "Fathom Press",
   "Fawcett Publications",
   "Feest Comics",
   "Felix Comics Inc.",
   "Femme Fatales Comics",
   "Fenickx Productions",
   "Ferret Press",
   "Fiasco Comics",
   "Fiction House",
   "Fiery Studios",
   "Filmation",
   "Fireman Press LTD.",
   "First",
   "First Salvo",
   "First Second Books",
   "Fishtales Inc Productions",
   "Fishwrap Production",
   "Fitzgerald Publishing Company",
   "Flaming Face Productions",
   "Fleetway",
   "Fluid Friction",
   "Fluide Glacial",
   "Forbidden Fruit",
   "Formatic",
   "Fortress Publishing",
   "Four Star Publications",
   "Fox",
   "Fox Atomic Comics",
   "Foxtrot",
   "Fragile Press",
   "Franco Cosimo Panini",
   "Frew Publications",
   "Friendly",
   "Frightworld",
   "Full Bleed Studios",
   "Full Circle Publications",
   "Full Impact Comics",
   "Full Stop Media",
   "Fun Publications",
   "Funk-O-Tron",
   "Funnies Inc",
   "Furio Viano Editore",
   "Futabasha Publishers Ltd.",
   "Future Comics",
   "FutureQuake Press",
   "Futuropolis",
   "G & T Enterprises",
   "G. Vincent Edizioni",
   "GG Studio",
   "Galassia",
   "Galaxinovels",
   "Galaxy Publishing",
   "Game Players Comics",
   "Games Workshop",
   "Gangan Comics",
   "Garage Graphix",
   "Gary Philips",
   "Gauntlet Comics",
   "Gaviota",
   "Gearbox Press",
   "Gebers",
   "Gem Publications",
   "Gemestone Publ.",
   "Gemstone",
   "General Electric Company",
   "Generation Comics",
   "Genesis West",
   "Genome Studios",
   "George A. Pflaum",
   "Georgia Straight",
   "Giant in the Playground",
   "Gilberton Publications",
   "Gilmor",
   "Gladstone",
   "Glenat Italia",
   "Globe Communications",
   "Gold Key",
   "Gold Star Publications Ltd.",
   "Golden Press",
   "Golfing / McCombs",
   "Good Comics, Inc",
   "Gotham Entertainment Group",
   "Granata Press",
   "Grand Central Publishing",
   "Graphic Arts Service, Inc.",
   "Graton Editeur",
   "Gratuitous Bunny Comix",
   "Great Big Comics",
   "Great Publications",
   "Great Smoky Mountains Historical Association",
   "Greater Mercury",
   "Green Man Press",
   "Green Publishing",
   "Grosset And Dunlap, Inc.,",
   "Ground Zero Comics",
   "Grupo Editorial Vid",
   "Guild Publications",
   "Gutsoon",
   "H. C. Blackerby",
   "H. H. Windsor",
   "HB Comics",
   "HELOCK COMICS",
   "HM Communications",
   "Hachette",
   "Hall Of Heroes",
   "Hallden",
   "Halloween",
   "Hamilton Comics",
   "Hammarstr",
   "Hamster Press",
   "Hand Of Doom Publications",
   "Handelsanst",
   "Happy Comics Ltd.",
   "Harpercollins",
   "Harperperennial",
   "Harrier",
   "Harris Comics",
   "Harry A. Chesler/Dynamic",
   "Harry N. Abrams",
   "Harvey",
   "Harvey Pekar",
   "Hasbro",
   "Hays Entertainment",
   "Headless Shakespeare Press",
   "Heavy Metal",
   "Helsinki Media",
   "Hemmets Journal Ab",
   "Heretic Press",
   "Hero Initiative",
   "Hero Universe",
   "Heroscribe Comics!",
   "Hershenson",
   "Hi No Tori Studio",
   "High Impact Entertainment",
   "High Top",
   "Highwater",
   "Highway 62 Press",
   "Hillman",
   "Holyoke",
   "Hot Comics",
   "Hound Comics",
   "Howard, Ainslee & Co.",
   "Hugh Lauter Levin Associates",
   "Humanoids",
   "Hurricane Entertainment",
   "Hyperwerks",
   "Hyperwrench Productions",
   "I.C.E. Comics",
   "I.W. Publishing",
   "IDW Publishing",
   "INFINITY Publishing",
   "INNFUSION",
   "IPC Magazines Ltd.",
   "Icarus Publications",
   "Ice Kunion",
   "Ideals Publishing",
   "If Edizioni",
   "Iguana Comics",
   "Illustrated Humor Inc",
   "Immortelle Studios",
   "Imperium Comics",
   "In the Public Domain",
   "Industrial Services",
   "Infinity Comics",
   "Infinity Studios",
   "Infocom",
   "Innovation",
   "Insight Editions",
   "Insomnia Press",
   "International Presse Magazine",
   "Iron Circus Comics",
   "Islas Filipinas Publishing Co.",
   "J",
   "JGM Comics",
   "Jabberwocky Graphix",
   "Jack Rabbit Stewdios",
   "Jademan",
   "Jemi F",
   "Jetpack Press",
   "Jeunesse Joyeuse",
   "Jochen Enterprises",
   "Joe Deagnon",
   "John Andersson",
   "Jump Back Productions",
   "Jump Comics",
   "JuniorPress BV",
   "Juvee Comics",
   "K",
   "Kadokawa Shoten",
   "Kana",
   "Kappa Edizioni",
   "Kathang Indio",
   "Kean Soo",
   "Keenspot Entertainment",
   "Ken Pierce Inc.",
   "Kenzer And Company",
   "Key Publications",
   "Kickstart Comics",
   "King Comics",
   "King Features Syndicate",
   "King Hell",
   "Kirby Publishing Company",
   "Kitchen Sink",
   "Kitty Publications",
   "Kk",
   "Knockabout",
   "Known Associates Press",
   "Kodansha",
   "Krause Publications",
   "Kyle Baker Publishing",
   "L",
   "L. Miller & Son, Ltd",
   "L.F.P.",
   "LFB Luigi F. Bona",
   "La Musardine",
   "La Repubblica / L'Espresso",
   "Lab Rat Productions",
   "Last Gasp",
   "Layne Morgan Media",
   "Le Lombard",
   "Leadbelly Publications",
   "Leader Enterprises",
   "Leading Edge Comics",
   "Lee Beardall",
   "Legion Of Evil Press",
   "Lego",
   "Lerner Publishing Group",
   "Les Editions Dargaud",
   "Lev Gleason",
   "Liar Comics",
   "Lightning Comics",
   "Lightspeed Press",
   "Lindblads F",
   "Lindqvists",
   "Linsner.com",
   "Lion King",
   "Lion Library",
   "Literacy Volunteers Of Chicago",
   "Literary Enterprises",
   "Little, Brown & Co.",
   "Lodestone",
   "Lohman Hills",
   "London Night Studios",
   "Lone Star Press",
   "Lost Cause Productions",
   "Lubrix",
   "Lucky Dragon Comics",
   "Lumen",
   "M. F. Enterprises",
   "MAD Books",
   "MDS Studios",
   "MJF Books",
   "MVCreation",
   "Mad Dog Graphics",
   "Mad Love Publishing",
   "Mad Monkey Press",
   "Maerkle Press",
   "Magazine Enterprises",
   "Magazine Management",
   "Magazzini Salani",
   "Magic Press",
   "Magnus & Bunker",
   "Majestic Entertainment",
   "Major Magazines",
   "Malmborg",
   "Manga 18",
   "Mango Comics",
   "Mansion Comics",
   "Manuscript Press",
   "Maple Leaf Publishing",
   "Mark",
   "Markosia",
   "Marsu Productions",
   "Martin L. Greim",
   "Max Bunker Press",
   "Maximum Press",
   "McCain Ellio's Comics",
   "McK Publishing",
   "McMann & Tate",
   "Mcfarland",
   "Media Press",
   "Media Works",
   "Megaton Comics",
   "Memory Lane Publication",
   "Mercury Comics",
   "Metro Comics",
   "Metropolitan Books",
   "Midnight Sons",
   "Mighty Comics",
   "Mighty Pumpkin",
   "Millennium Publications",
   "Milson",
   "Mina Editores",
   "Mindgame Press Page One, Inc.",
   "Mirage",
   "Modern",
   "Mojo Press",
   "Mondial",
   "Monkeysuit Press",
   "Monster Comics",
   "Monsterverse",
   "Moonface Press",
   "Moonstone",
   "Morning Star Productions",
   "Mosaik Steinchen F",
   "Motorcycleboy Comics",
   "Mr. Comics",
   "Mu Press",
   "Mulehide Graphics",
   "Murray Comics",
   "NFPA",
   "Naked City",
   "Narwain",
   "Nate Butler",
   "Nation-Wide comics",
   "National Comics Publication",
   "National Comics Publications",
   "National Comics Publishing",
   "National Periodical Publications",
   "National Periodical Publications Inc",
   "Nationella Trafiks",
   "Nedor",
   "Neko Press",
   "NeoSun",
   "Neuer Tessloff Verlag",
   "New American Library",
   "New Comics Group",
   "New England Comics",
   "New Media Publications",
   "New Universe",
   "New Worlds",
   "Newsbook Publishing",
   "Newspaper: Funny Pages",
   "Nickel Editions",
   "Nicotat",
   "Night Wynd Enterprises",
   "No Mercy",
   "Noble Comics",
   "Norbert Hethke Verlag",
   "Norma Editorial",
   "Normans",
   "Northstar",
   "Nostalgia Press",
   "Novaris Entertainment",
   "Novedades Editores",
   "Novelty Press",
   "Now",
   "Ocean Comics",
   "Odhams Press",
   "Odyssey Comics",
   "Ok",
   "Oktomica",
   "Olio",
   "Olympian Publishing",
   "Olyoptics",
   "Oni Press",
   "Opal",
   "Orang Utan Comics",
   "Ordfront",
   "Orin Books",
   "Oscar Caesar",
   "Oval Projects Limited",
   "P.F. Volland Company",
   "PSG Publishing House",
   "Pacific",
   "Pacific Comics",
   "Palisades Press",
   "Palliard Press",
   "Pan",
   "Pandora Press",
   "Panini Comics",
   "Pantheon Books",
   "Paper Dragonz",
   "Paper Street Comics",
   "Paper Tiger Comics",
   "Paper Tiger Comix",
   "Papyrus Comics",
   "Paquet",
   "Parents",
   "Parker Editore",
   "Parody Press",
   "Penny Farthing",
   "Pentagon Publishing Co",
   "Penthouse Comics",
   "Peregrine Entertainment",
   "Personality",
   "Phelps Publishing",
   "Phi3 Comics",
   "Philomel Books",
   "Phoenix Fire Studios",
   "Picturebox",
   "Pied Piper",
   "Pines Comics",
   "Pingvinf",
   "Pinnacle Comics",
   "Pioneer Books Inc.",
   "Planet Comics",
   "Planet Publishing",
   "Planeta DeAgostini",
   "Platinum Studios Comics",
   "Play Press",
   "Playboy Press",
   "Pocket Books",
   "Point G Comics",
   "Politisk Revy",
   "Polystyle",
   "Pop Comics",
   "Popular Press",
   "Poseur Ink",
   "Possum Press",
   "Power Comics",
   "Power Records",
   "Praxis Comics",
   "Premier Magazines",
   "Pride Comics",
   "Primal Paper Comics",
   "Print Mint",
   "Prize",
   "Progressive",
   "Promotora K",
   "Publicaciones Herrerias",
   "Publication Enterprises",
   "Publistrip",
   "Pughouse Press",
   "Pulp Theatre",
   "Pure Imagination",
   "Purrsia",
   "Pyramid Communications",
   "Q Comics",
   "Quality Comics",
   "Quality Periodicals",
   "RAK Graphics",
   "RCS MediaGroup",
   "RDS Comics",
   "RSquared Studios",
   "Rab",
   "Rabbit Valley",
   "Radbu Productions",
   "Radical Publishing",
   "Radio Comics",
   "Rainbow Media",
   "Raj Comics",
   "Ralston-Purina Company",
   "Random House",
   "Rat Race Comix",
   "Real",
   "Real Free Press",
   "Realistic",
   "Realm Press",
   "Rebel Studios",
   "Rebellion",
   "Recollections",
   "Red 5 Comics",
   "Red Circle",
   "Red Clown",
   "Red Eagle Entertainment",
   "Red Top",
   "Redbud Studio",
   "Redhead Comics",
   "Regor Company",
   "Renaissance Press",
   "Renegade",
   "Reprodukt",
   "Revolutionary",
   "Rheem Water Heating",
   "Richters F",
   "Rip Off Press",
   "Rippu Shobo",
   "Robert laffont",
   "Rocket North Publishing",
   "Roger Corman's Cosmic Comics",
   "Ronin Studios",
   "Rooster Teeth Productions",
   "Rorschach Entertainment",
   "Rotopress",
   "Rude Dude Productions",
   "Running Press",
   "Rural Home",
   "Russ Cochran",
   "Rutledge Hill Press",
   "S",
   "SANS Entertainment Comics",
   "SNK Playmore",
   "SQP",
   "Saalfield Publishing Company",
   "SaberCat Comics",
   "Sackmann Und H",
   "Sacred Mountain",
   "Saint James",
   "Salvatore Taormina editore",
   "Sanoma Uitgevers",
   "Saxon",
   "Say/Bart Productions",
   "Scar Comics",
   "Schibsted",
   "Scholastic Book Services",
   "Schultz",
   "Scrap Pictures",
   "Se-Bladene",
   "Seaboard Publishing",
   "Second To Some",
   "Semic As",
   "Semic International",
   "Sergio Bonelli Editore",
   "Seven Seas Entertainment",
   "Shanda Fantasy Arts",
   "Shibalba Press",
   "Shinshokan",
   "Shivae Studios",
   "Shogakukan",
   "Shooting Star",
   "Showcase Publications",
   "Shueisha",
   "Sig Feuchtwanger",
   "Signet Books",
   "Silent Devil Productions",
   "Silent Nemesis Workshop",
   "SilverWolf",
   "Silverline",
   "Simon And Schuster",
   "Sirius Entertainment",
   "Skandinavisk Press",
   "Skatoon Productions",
   "Skywald",
   "Sleeping Giant Comics",
   "Sm",
   "Smithsonian Institution",
   "Softbank Creative",
   "Solson Publications",
   "Sombrero",
   "Son of Sam Productions",
   "Sound & Vision International",
   "Space Goat Productions",
   "Spacedog",
   "Spark Publications",
   "Speakeasy Comics",
   "Special Action Comics",
   "Special Studio",
   "Spectrum Comics",
   "Spilled Milk",
   "Spire Christian Comics",
   "Splitter",
   "Spotlight Comics",
   "Spotlight Publishers",
   "St",
   "St. Johns Publishing Co.",
   "Stampa Alternativa / Nuovi Equilibri",
   "Stanhall",
   "Stanley Publications",
   "Stanmor Publications",
   "Star",
   "Star Publications",
   "Star Reach Publications",
   "Starhead Comix",
   "Stats Etc",
   "Sterling",
   "Stopdragon",
   "Storm Lion Publishing",
   "Story Comics",
   "Straw Dog",
   "Strawberry Jam Comics",
   "Street & Smith",
   "Street And Smith",
   "Street and Steel",
   "Striker 3D",
   "Studio 407",
   "Studio Aries",
   "Studio Foglio",
   "Studio Insidio",
   "Studio Ironcat",
   "Super Publishing",
   "Superior Publishers Limited",
   "Sussex Publishing Co",
   "Svenska Serier",
   "Swappers Quarterly And Almanac",
   "T.R.I.B.E. Studio Comics",
   "TSR",
   "Ta Nea",
   "Tapestry",
   "Tekno Comix",
   "Tell Tale Publications",
   "Tempo Books",
   "Terminal Press",
   "Terra Major",
   "Terzopoulos",
   "Teshkeel Comics",
   "Tetragrammatron",
   "Th3rd World",
   "The 3-D Zone",
   "The Comic Times, Inc.",
   "The Heritage Collection",
   "The Scream Factory",
   "The Toy Man",
   "Thorby Enterprises",
   "Thoughts",
   "Thrill-House Comics",
   "Thunder Baas",
   "Time Bomb Comics",
   "Timeless Journey Comics",
   "Timely",
   "Timely Illustrated Features",
   "Tipografia M. Tomasina",
   "Titan Books",
   "Titan Magazines",
   "Toby",
   "Tom Doherty Associates",
   "Tom Stacey",
   "Tome Press",
   "Top Cow",
   "Top Shelf",
   "Topps",
   "Torpedo Comics",
   "Toutain Editor",
   "Tower",
   "Tower Books",
   "Transfuzion Publishing",
   "Transmission X Comics",
   "Trepidation Comics",
   "Trident Comics",
   "Trigon",
   "Triumph",
   "Triumphant",
   "Triumphant Comics",
   "Trojan",
   "True Believers Press",
   "True Patriot Studios",
   "Tumble Creek Press",
   "Tundra",
   "Tundra Uk",
   "Tusquets Editores",
   "Twomorrow",
   "Tyler James Comics",
   "UDON",
   "US Department of Health, Education and Welfare",
   "Uitgeverij C.I.C.",
   "Ultimate Comic Group",
   "Ultimate Creations",
   "Ultimate Sports Force",
   "Ungdomsmissionens V",
   "Unified Field Operations",
   "United Features",
   "Universe",
   "Utslag",
   "Utterly Strange Publications",
   "Valiant",
   "Valve",
   "Vanguard Productions",
   "Vents d'Ouest",
   "Vermillon",
   "Verotik",
   "Vertical Inc.",
   "Victor Gollancz Ltd.",
   "Victory",
   "View Askew",
   "Viper Comics",
   "Virgin Comics",
   "Virus Comix",
   "Vittorio Pavesio Productions",
   "Vivid Publishing",
   "Viz",
   "Viz Premiere",
   "Viz Select",
   "Vortex",
   "Vrijbuiter, De",
   "W.T. Grant",
   "WCG",
   "WSOY",
   "Wallace Wood",
   "Walt Disney Company Italia",
   "Warner Books",
   "Warner Brothers",
   "Warp Graphics",
   "Warren",
   "Warrior Publications",
   "Watson-Guptill Publications",
   "Webs Adventure Corporation",
   "Welsh Publishing Group",
   "Western Publishing.",
   "White Buffaloe Press",
   "White Lightning Productions",
   "Whitman",
   "Whitman Publishing",
   "Wicked Good Comics",
   "Wild and Wooly Press",
   "Wildcard Production",
   "William H Wise",
   "Williams F",
   "Willms Verlag",
   "Windjammer",
   "Winthers",
   "Wisconson Department Of justice",
   "Wonder Comix",
   "Work Horse Comics",
   "XL Creations",
   "Xanadu Publishing, Inc.",
   "Yen Press",
   "Yendie Book Publishing",
   "Yoe Studio",
   "Youthful",
   "ZOOLOOK",
   "Zenescope Entertainment",
   "Ziff",
   "Ziff Davis Media",
   "Zip Comics",
   "Zodiac",
   "Zuzupetal Press",
   "Zwerchfell",
   "comicsone.com",
   "eBay",
   "ffantasy ffactory",
   "iVerse Media",
   "inZane Comics",
   "mg/publishing",
   "self published",
   "talcMedia Press",
   "¡Ka-Boom! Estudio S.A. de C.V.",
])



# =============================================================================
if __name__ == '__main__':
   '''
   A script method that can be run to compare the contents of the tables in this
   module with the publishers listed in the ComicVine database.  This script
   should be run periodically, and used to update the tables in this module.
   '''
   
   # first, gather the names of all the publishers on the ComicVine database
   # by scraping them and adding them to a set of scraped publishers
   log.debug()
   print "Gathering publishers from ComicVine..."
   scraped_publishers = set()
   
   done = False
   page = 0
   while not done:
      page += 1
      html = ""
      try:
         request = WebRequest.Create(
            'http://www.comicvine.com/publishers/?page='
            + sstr(page) + '&sort=alphabetical')
         response = request.GetResponse()
         responseStream = response.GetResponseStream()
         reader = StreamReader(responseStream, Text.Encoding.UTF8)
         html = reader.ReadToEnd()
      except WebException, wex:
         print("unexpected web exception: " + str(wex)) 
      finally:
         if 'reader' in vars(): reader.Close()
         if 'responseStream' in vars(): responseStream.Close()
         if 'response' in vars(): response.Close()
         
      writer = StringWriter() # coryhigh: make this into a utility method
      HttpUtility.HtmlDecode(html, writer)
      html = writer.ToString()
      matches =set( [m.strip() for m in 
         re.findall("(?m)<td[^>]*>\s*<a[^>]*>([^<]*)</a>\s*</td>",html) ] )
      done = matches <= scraped_publishers # stop when we are repeating results
      if not done:
         scraped_publishers.update( matches )
         print"Page " + sstr(page) + ", " + sstr(len(matches))+" publishers..."
   
   # 2. now that we've got all the publishers on ComicVine, go through our 
   #    know publishers, and report a) if we have one that isn't in ComicVine
   #    anymore, and b) if ComicVine now has one that we don't.
   all_clear = True 
   print("")  
          
   for imprint in __imprint_map:
      if imprint not in scraped_publishers:
         all_clear = False 
         print("Not in ComicVine: " + imprint)
         
   for publisher in __other_publishers:
      if publisher not in scraped_publishers:
         all_clear = False 
         print("Not in ComicVine: " + publisher)
         
   for publisher in sorted(scraped_publishers):
      if publisher not in __imprint_map and publisher not in __other_publishers:
         all_clear = False 
         print("Not in module: " + publisher)

   if all_clear:
      print("Nothing to update!")