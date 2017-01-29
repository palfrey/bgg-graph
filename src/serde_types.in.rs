#[derive(Deserialize, Debug, PartialEq)]
pub struct Name {
    #[serde(rename = "type")]
    pub type_: String,  
    pub sortindex: i32,
    pub value: String, 
}

#[derive(Deserialize, Debug, PartialEq)]
pub struct IntValue {
    pub value: i32
}

#[derive(Deserialize, Debug, PartialEq)]
pub struct Result {
    pub value: String,
    pub numvotes: i32
}

#[derive(Deserialize, Debug, PartialEq)]
pub struct Results {
    pub numplayers: String,
    pub result: Vec<Result>
}

#[derive(Deserialize, Debug, PartialEq)]
pub struct Poll {
    pub name: String,
    pub title: String,
    pub totalvotes: i32,
    pub results: Vec<Results>
}

#[derive(Deserialize, Debug, PartialEq)]
pub struct Item {
    pub image: String,
    #[serde(rename = "type")]
    pub type_: String,   
    pub id: String,
    pub thumbnail: String,
    pub name: Vec<Name>,
    pub description: String,
    pub yearpublished: IntValue,
    pub minplayers: IntValue,
    pub maxplayers: IntValue,
    pub poll: Vec<Poll>,
    pub playingtime: IntValue,
    pub minplaytime: IntValue,
    pub maxplaytime: IntValue,
    pub minage: IntValue,
}

#[derive(Deserialize, Debug, PartialEq)]
pub struct Items {
    pub termsofuse: String,
    pub item: Vec<Item>,
}