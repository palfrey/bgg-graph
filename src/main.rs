extern crate serde_xml;
use std::env;
use std::fs::File;
use std::io::Read;
extern crate serde;

mod types;

fn main() {
    let path = env::args().nth(1).unwrap();
    let mut f = File::open(path).unwrap();
    let mut s = String::new();
    f.read_to_string(&mut s).unwrap();
    let result: types::Items = serde_xml::de::from_str(&s).unwrap();
    println!("{:?}", result);
}
