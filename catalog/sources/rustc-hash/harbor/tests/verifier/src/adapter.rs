use rustc_hash::{FxBuildHasher, FxHashMap, FxHashMapSeed, FxHashSet, FxHashSetSeed, FxHasher, FxSeededState};
use std::hash::{BuildHasher, Hash, Hasher};
use std::io::{self, BufRead};

fn hash<T: Hash>(value: T) -> u64 { let mut h = FxHasher::default(); value.hash(&mut h); h.finish() }
fn seeded(seed: usize, value: u64) -> u64 { let mut h = FxSeededState::with_seed(seed).build_hasher(); value.hash(&mut h); h.finish() }
fn check(i: usize) -> bool { match i {
    1 => hash(b"rustc-hash" as &[u8]) != 0, 2 => hash(1u8) == hash(1u16), 3 => hash(-1i64) != 0,
    4 => hash(&[] as &[u8]) != hash(b"cafe" as &[u8]), 5 => seeded(7, 1) == seeded(7, 1),
    6 => FxBuildHasher.build_hasher().finish() == FxHasher::default().finish(),
    7 => { let mut m: FxHashMap<&str,u32>=FxHashMap::default();m.insert("a",1);m.get("a")==Some(&1) },
    8 => { let mut m: FxHashMap<&str,u32>=FxHashMap::default();m.insert("a",1);m.insert("a",2);m.remove("a")==Some(2) },
    9 => { let mut s: FxHashSet<u32>=FxHashSet::default();s.insert(4) }, 10 => { let mut s: FxHashSet<u32>=FxHashSet::default();s.insert(4);s.contains(&4)&&s.remove(&4) },
    11 => { let mut m: FxHashMap<u32,u32>=FxHashMap::default();m.insert(1,2);m.insert(3,4);m.values().sum::<u32>()==6 }, 12 => { let mut s: FxHashSet<u32>=FxHashSet::default();s.extend([1,2,3]);s.iter().sum::<u32>()==6 },
    13 => seeded(3,9)==seeded(3,9), 14 => seeded(1,9)!=seeded(2,9), 15 => hash(1u8)==hash(1u16), 16 => hash(9u32)==hash(9u64),
    17 => hash(9u128)!=hash(9usize), 18 => { let mut h=FxHasher::default();h.write_u64(55);let x=h.finish();h.finish()==x }, 19 => hash("a")!=hash("b"),
    20 => { let mut m:FxHashMap<u32,u32>=FxHashMap::default();m.insert(1,1);m[&1]==1 }, 21 => { let mut m:FxHashMapSeed<u32,u32>=FxHashMapSeed::with_hasher(FxSeededState::with_seed(3));m.insert(1,1);let mut s:FxHashSetSeed<u32>=FxHashSetSeed::with_hasher(FxSeededState::with_seed(3));s.insert(1);m[&1]==1&&s.contains(&1) },
    22 => true, 23 => hash("api") != 0, 24 => true, _ => false }}
fn main() { for line in io::stdin().lock().lines() { let i:usize=line.unwrap().parse().unwrap(); println!("{}",if check(i){"ok"}else{"fail"}); } }
