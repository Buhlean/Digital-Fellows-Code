import Browser
import Html exposing (Html, text, pre, div, input, button, ul, li, span, b)
import Html.Attributes as A
import Html.Events exposing (onClick, onInput, onDoubleClick)
import Http
import XmlParser exposing (Node(..))

main 
  = Browser.element
  { init = init
  , update = update
  , subscriptions = subscriptions
  , view = view
  }

type alias Cue =
  { start : Float
  , duration : Float
  , content : String
  }

type alias Model = 
  { input_field : String
  , jump_to_position : (Int, Float)
  , state : State
  }

type State
  = Please_Input_ID Bool
  | Loading_XML String
  | Load_Failure
  | Parse_Failure
  | Success String (List Cue) 
  | Editing String (List Cue) Int

type Msg
  = ID_Changed String
  | Cue_Changed Int String
  | Fetch_Default
  | Validate_And_Fetch
  | GotAnswer (Result Http.Error String)
  | JumpTo (Int, Float)
  | Summon_Editor Int

-- INIT --
init : () -> (Model, Cmd Msg)
init _ = (
  { input_field = ""
  , jump_to_position = (0, 0.0)
  , state = (Please_Input_ID True)
  },
  Cmd.none)

-- UPDATE --
update : Msg -> Model -> (Model, Cmd Msg)
update msg model =
  case model.state of
    Success id cues -> 
      case msg of
        ID_Changed new      -> ({model | input_field = new }                                                          , Cmd.none)
        Fetch_Default       -> ({model | state = (Loading_XML "default") }                                            , fetch_default_transcript)
        Validate_And_Fetch  -> case validate_id model.input_field of
            Ok video_id     -> ({model | state = (Loading_XML video_id) }                                             ,(fetch_transcript video_id))
            Err _           -> ({model | state = Please_Input_ID False }                                              , Cmd.none)
        JumpTo info         -> ({model | jump_to_position = info }                                                    , Cmd.none) -- @TODO: tell the youtube player where to jump
        Summon_Editor who   -> ({model | state = (Editing id cues who) }                                              , Cmd.none)
        _                   -> ( model                                                                                , Cmd.none)
    Editing id cues index   -> case msg of
        ID_Changed new      -> ({model | state = Success id cues, input_field = new }                                 , Cmd.none)
        Cue_Changed who new -> ({model | state = (Editing id (List.indexedMap (update_if new who) cues) index) }     , Cmd.none)
        Fetch_Default       -> ({model | state = (Loading_XML "default") }                                            , fetch_default_transcript)
        Validate_And_Fetch  -> case validate_id model.input_field of
            Ok video_id     -> ({model | state = (Loading_XML video_id) }                                             ,(fetch_transcript video_id))
            Err _           -> ({model | state = Please_Input_ID False }                                              , Cmd.none)
        JumpTo info         -> ({model | jump_to_position = info , state = Success id cues}                           , Cmd.none) -- @TODO: tell the youtube player where to jump
        Summon_Editor who   -> ({model | state = (Editing id cues who) }                                              , Cmd.none)
        _                   -> ( model                                                                                , Cmd.none)
    Loading_XML id          -> case msg of
        GotAnswer result    -> case result of
            Ok fullText     -> case parse_xml fullText of 
                Nothing     -> ({model | state = Parse_Failure }                                                      , Cmd.none)
                Just cues   -> ({model | state = Success id cues }                                                    , Cmd.none)
            Err _           -> ({model | state = Load_Failure }                                                       , Cmd.none)
        ID_Changed new      -> ({model | state = (Please_Input_ID True), input_field = new }                          , Cmd.none)
        _                   -> ( model                                                                                , Cmd.none)
    _ -> -- Please_Input_ID, Load_Failure, Parse_Failure:
      case msg of
        ID_Changed new      -> ({model | state = (Please_Input_ID True), input_field = new }                          , Cmd.none)
        Fetch_Default       -> ({model | state = (Loading_XML "default") }                                            , fetch_default_transcript)
        Validate_And_Fetch  -> case validate_id model.input_field of
            Ok video_id     -> ({model | state = (Loading_XML video_id) }                                             ,(fetch_transcript video_id))
            Err _           -> ({model | state = Please_Input_ID False }                                              , Cmd.none)
        _                   -> ( model                                                                                , Cmd.none)

-- Helper
type Error
  = BadInput
  | NotAYtURL
  | EmptyString
  
validate_id : String -> Result Error String
validate_id input = 
  if String.isEmpty input then
    Err EmptyString
  else if ((String.length input) < 15) && ((String.length input) > 10) then
    Ok input
  else if String.contains "youtu.be" input then
    butcher_URL input ".be/" "?" BadInput
  else if String.contains "youtube" input then
    if String.contains "/v/" input then
      butcher_URL input "/v/" "?" BadInput
    else if String.contains "/watch?v=" input then
      butcher_URL input "/watch?v=" "&" BadInput
    else
      Err NotAYtURL
  else
    Err NotAYtURL

butcher_URL : String -> String -> String -> Error -> Result Error String
butcher_URL url cut1 cut2 error =
  case (String.split cut1 url) of
      head::tail::[] -> 
        case (String.split cut2 tail) of
          id::xs -> Ok id
          _ -> Err error
      _ -> Err error

update_if : String -> Int -> Int -> Cue -> Cue
update_if new_content only_this_one_gets_changed current_index current_cue = 
  if current_index == only_this_one_gets_changed then
    { current_cue | content = new_content }
  else
      current_cue  

fetch_default_transcript : Cmd Msg
fetch_default_transcript 
  = Http.get
  { url = "https://raw.githubusercontent.com/Buhlean/LiaPresentations/master/XML/gates_virus_example_captions.xml"
  , expect = Http.expectString GotAnswer
  }
fetch_transcript : String -> Cmd Msg
fetch_transcript video_id 
  = Http.get
  { url = "https://video.google.com/timedtext?v=" ++ video_id ++ "&lang=en"
  , expect = Http.expectString GotAnswer
  }

-- SUB --
subscriptions : Model -> Sub Msg
subscriptions model = Sub.none

-- VIEW --
view : Model -> Html Msg
view model =
  case model.state of
    Please_Input_ID valid ->
      div [A.style "width" "100ch"] [ (field_and_buttons model False "") ]
    Loading_XML _ ->
      div [A.style "width" "100ch"] [ (field_and_buttons model False "Loading...") ]
    Load_Failure ->
      div [A.style "width" "100ch"] [ (field_and_buttons model False "Sorry, couldn't find transcript!") ]
    Parse_Failure ->
      div [A.style "width" "100ch"] [ (field_and_buttons model False "Sorry, couldn't parse transcript!") ]
    Success video_id cues -> 
      div [A.style "width" "100ch"] [ 
        (field_and_buttons model True ("Loaded: "++video_id)),  
        div (
          [ A.id "cues-container"
          ]++common_style_text
           ++common_style_container) (List.indexedMap (generate_html_from_cue (Tuple.first model.jump_to_position) Nothing) cues)
        ]
    Editing video_id cues index ->
      div [A.style "width" "100ch"] [
        (field_and_buttons model True ("Loaded: "++video_id)),
        div (
          [ A.id "cues-container"
          ]++common_style_text
           ++common_style_container) (List.indexedMap (generate_html_from_cue (Tuple.first model.jump_to_position) (Just index)) cues)
        ]

field_and_buttons : Model -> Bool ->  String -> Html Msg
field_and_buttons model player_controls message = 
  if player_controls then
    div  [] 
      [ div [] [(url_field model.input_field), fetch_button, fetch_default_button, (status_message message)]
      , div [ A.style "height" "1.8em", A.style "position" "relative", A.style "margin" "4px" ] 
        [ div  
          [ A.style "font-size" "1.8em"
          , A.style "margin" "4px"
          , A.style "display" "inline-block"
          , A.style "position" "absolute"
          , A.style "left" "0px"
          ] [ text ("Jump to: " ++ (String.fromFloat (Tuple.second model.jump_to_position))) ]
        , div  
          [ A.style "font-size" "0.9em"
          , A.style "margin" "1px"
          , A.style "display" "inline-block"
          , A.style "position" "absolute"
          , A.style "right" "0px"
          , A.style "width" "18ch"
          ] [ text "Click to jump, DoubleClick to edit." ]
        ]
      ]
  else 
    div  [] [ div [] [(url_field model.input_field), fetch_button, fetch_default_button, (status_message message)]]

common_style_top : (List (Html.Attribute Msg))
common_style_top = 
  [ A.style "margin" "4px"
  , A.style "font-size" "1.1em"
  , A.style "padding" "1px"
  ]
common_style_text : (List (Html.Attribute Msg))
common_style_text =
  [ A.style "font-size" "1.1em"
  , A.style "color" "#000"
  , A.style "font-family" "Arial"
  ]
common_style_container : (List (Html.Attribute Msg))
common_style_container =
  [ A.style "overflow-y" "auto"
  , A.style "height" "40vh"
  , A.style "margin" "8px"
  , A.style "border" "1px solid black"
  ]
  
url_field : String -> Html Msg
url_field id = input (
  [ A.placeholder "Please provide a YouTube video link."
  , A.value id
  , onInput ID_Changed
  , A.id "input-video-url-or-id"
  , A.style "min-width" "32ch"
  ]++common_style_top) []

fetch_button : Html Msg
fetch_button = button (
  [ onClick Validate_And_Fetch
  , A.id "button-fetches-transcript-by-id"
  ]++common_style_top) [ text "Fetch transcript" ]

fetch_default_button : Html Msg
fetch_default_button = button (
  [ onClick Fetch_Default
  , A.id "buttone-fetches-sample-transcript"
  ]++common_style_top) [ text "Click Me!" ]

status_message : String -> Html Msg
status_message message = span (
  [ 
  ]++common_style_top) [b [] [text message]]

generate_html_from_cue : Int -> (Maybe Int) -> Int -> Cue -> Html Msg
generate_html_from_cue highlit editing index cue = 
  case editing of
    Nothing -> (create_cue_span index cue)
    Just number -> if index == number then 
      create_editable_cue index cue
      else
        (create_cue_span index cue)
create_cue_span : Int -> Cue -> Html Msg
create_cue_span index cue =  
  span 
    [ onClick (JumpTo (index, cue.start))
    , onDoubleClick (Summon_Editor index)
    , A.id ("cue-"++ (String.fromInt index))
    , A.class "cue"
    ] [ text cue.content ]
create_editable_cue : Int -> Cue -> Html Msg
create_editable_cue index cue =
  input (
    [ onInput (Cue_Changed index)
    , onDoubleClick (JumpTo (index, cue.start))
    , A.id ("input-cue-"++ (String.fromInt index))
    , A.class "cue-input"
    , A.value cue.content
    , A.style "min-width" (String.fromInt (round((toFloat(String.length cue.content))*0.8))++"ch")
    ]++common_style_text) []
{--
Output from XmlParser.parse on a subset of my data for function building purposes:

> import XmlParser
> XmlParser.parse """<?xml version="1.0" encoding="UTF-8"?><transcript><text start="17.504" dur="1.894">When I was a kid,</text><text start="19.398" dur="3.561">the disaster we worried about most was a nuclear war.</text><text start="23.819" dur="3.266">That&amp;#39;s why we had a barrel like thisdown in our basement,</text></transcript>"""

Ok  { docType                 = 
        Nothing
    , processingInstructions  = 
        [ { name = "xml", value = "version=\"1.0\" encoding=\"UTF-8\"" } ]
    , root                    = 
        Element "transcript" [] [
        Element "text" [
          { name = "start"
          , value = "17.504" 
          }
        , { name = "dur"
          , value = "1.894" 
          }
        ] 
        [ Text ("When I was a kid,")]
        , Element "text" [
          { name = "start"
          , value = "19.398" 
          }
        , { name = "dur"
          , value = "3.561" 
          }
        ] 
        [ Text ("the disaster we worried about most was a nuclear war.")]
        , Element "text" [
          { name = "start"
          , value = "23.819" 
          }
        , { name = "dur"
          , value = "3.266" 
          }
        ] 
        [ Text ("That&#39;s why we had a barrel like this down in our basement,")]
      ] 
    }
: Result (List XmlParser.DeadEnd) XmlParser.Xml
--}

parse_xml : String -> Maybe (List Cue)
parse_xml xml = 
  case XmlParser.parse xml of
    Err error ->
      Nothing
    Ok result ->
      case result.root of 
        (Text text) ->
          Nothing -- pleases the compiler
        (Element text attributes cue_nodes) ->
          Just (empty_cue :: (corral_cues cue_nodes))

corral_cues : List Node -> List Cue
corral_cues nodes = 
  case nodes of
    [] -> []
    [cue] -> 
      [extract_information cue]
    cue::xs ->
      case cue of
        Text text ->
          corral_cues xs
        Element text attr content ->
          [extract_information cue] ++ corral_cues xs

empty_cue : Cue
empty_cue = {start=0.0, duration=0.0, content=">> "}

toFloat_with_default : String -> Float -> Float
toFloat_with_default string def =
  case String.toFloat string of
    Nothing    -> def
    Just value -> value
  
extract_information : Node -> Cue
extract_information node =
  case node of
    Element _ ( start_attr :: duration_attr :: []) (( Text cue_text) :: []) ->
      { start    = (toFloat_with_default start_attr.value 0.0)
      , duration = (toFloat_with_default duration_attr.value 0.0)
      , content  = ((String.replace "&#39;" "'" cue_text) ++ " ")
      }
    _ -> empty_cue
