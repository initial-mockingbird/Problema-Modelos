# Dark Souls Problem

## Read the spanish version at: [Español](README.spa.md)

## Narrative
In the Age of Ancients the world was unformed, shrouded by fog. A land of gray crags, Archtrees and Everlasting Dragons. But then there was Fire and with fire came disparity. Heat and cold, life and death, and of course, light and dark. Then from the dark, They came, and found the Souls of Lords within the flame.

Thus began the Age of Fire. But soon the flames will fade and only Dark will remain. Even now there are only embers, and man sees not light, but only endless nights. And amongst the living are seen, carriers of the accursed Darksign.

You are the chosen undead, destined to rekindle the fire, but to do so, you need to consume the dark souls to gain power.

There are currently 3 locations which soul farming is most profitable, each location offers better rewards based on one of the three major skills: `strength`, `dexterity` and `item discovery`.

## Locations

### High Wall of Lothric

![High Wall of Lothric](./imgs/high_wall_of_lothric.jpg)

Home of knights, the High wall of Lothric presents the perfect place to earn souls for `strength` oriented builds while also punishing the `Dex` oriented builds, after countless runs, it was determined that the number of souls yielded per run follows the following formula:

```haskell
souls_lothric :: (Int,Int,Int) -> Float
souls_lothric (str,dex,item_discovery) = str_earned + dex_earned + total_items
    where
        str_earned = 3*str
        dex_earned = (-11)*dex/7
        high_items = (item_discovery/4)
        mid_items  = 5*(item_discovery/4)
        low_items  = 3*(item_discovery/2)
        total_items= high_items + mid_items + low_items
```


### New Londo Ruins

![New Londo Ruins](./imgs/new_londo_ruins.jpg)

New Londo, once a great city, now resides forgotten in the bottom of a flooded pit, thus a combination of `strength` and `dexterity` is required in order to beat the challenges it poses, through trial and error, it was determined that the number of souls yielded per run is:

```haskell
souls_londo :: (Int,Int,Int) -> Float
souls_londo (str,dex,item_discovery) = combined_earned + total_items
    where
        combined_earned = (str*dex) - 2*(str+dex)
        high_items = 3*(item_discovery/5)
        mid_items  = 2*(item_discovery/4)
        low_items  = (11*item_discovery/20)
        total_items= high_items + mid_items + low_items
```

### The Duke's Archives

![The Duke's Archives](./imgs/dukes_archives.jpg)

The Duke's archives: a giant desolated library complex whose treasures are free for the brave, thus it greatly favors the `item discovery` skill, the number of souls each run yields is given by:

```haskell
souls_archives :: (Int,Int,Int) -> Float
souls_archives (str,dex,item_discovery) = str_earned + dex_earned + total_items + 300
    where
        str_earned = -str
        dex_earnet = 5*dex/2
        high_items = 3*(item_discovery/2) 
        mid_items  = (item_discovery/2)
        total_items= high_items + mid_items
```

## Mechanic: Leveling up

Up till now, we have talked about how each place is influenced by the skill level of the character, but we haven't talked about how the character grows.

In order to level up and earn a skill point (which increases a particular skill by 1), the chosen undead must pay a price in souls equal to the following relation:

```haskell
level_up :: (Int,Int) -> Int
level_up(new_levels,total_levels) = new_levels*total_levels/300 + 5*new_levels
```

## Goal and inital specs:

The goal is maximizing the number of souls at the `n-th` run, provided that the chosen undead starts with the following stats:

```haskell
Base_Stats = {
    Str: 3,
    Dex: 2,
    Item: 3,
    Initial Souls: 200
}
```

## Results

After solving the problem for $n = 1 \dots 7$, we collected the results in the following table:

| Run # | obj_max | total str | total dex | total item | Fav Place              |
|-------|---------|-----------|-----------|------------|------------------------|
| 1     | 513     | 0         | 0         | 0          | archives (1)           |
| 2     | 826     | 0         | 0         | 0          | archives (2)           |
| 3     | 1179    | 0         | 0         | 40         | archives (3)           |
| 4     | 1638    | 0         | 0         | 116        | archives (4)           |
| 5     | 2246    | 0         | 0         | 177        | archives(5)            |
| 6     | 3182    | 0         | 0         | 347        | archives(3), lotrhic(3) |
| 7     | 4732    | 78        | 0         | 400        | archives(3), lotrhic(4) |

Which presents an interesting idea, you see, most games follows a logical trend: the optimal build is either a _pure_ build (focusing on a single skill), or an _hybrid_ build (focusing in 2 skills), but in this case, the program determined that the best course of action was beggining as a _pure item discovery_, and after reaping the rewards of the archives, branching into an _hybrid item/str_.

This yields an interesting insight over the problem: whenever we have a problem that feeds itself the resources, it will try to minimize the rentability by itself, so sensibility analysis isn't strcitly necessary, we can just run another iteration a watch the results.


## Modeling Process (Optional)

### The ~~Axiom~~ of Choice:

Lets study the case for just 1 day, we naively might suggest that the total number of souls earned for day 1 would be (abusing the notation a little):

```C
base_souls                              +
souls_lothric(base_stats+leveled_stats) + 
souls_londo(base_stats+leveled_stats)   + 
souls_archive(base_stats+leveled_stats) -
level_up(#base_stats,#leveled_stats)
```

Nevertheless, on closer inspection this is clearly wrong for a very precise reason: we cannot visit multiple places in the same run, we must **choose exactly one** location.

Thankfully the way we model `election` is simple, let's say we have two actions: `a_1` and `a_2`, then:

```C
max/min z = e_1 * a_1 + e_2*a_2
```

Subject to:

```C
e_1*e_2 = 0
e_1+e_2 = 1
```

Perfectly models the predicate: you can do `a_1` or `a_2` but not both, this is because of the restrictions, since if `e_1*e_2 = 0` then either:

* `e_1 = 0`, and thus `max/min z = 0 * a_1 + e_2 *a_2 = e_2*a_2`
* `e_2 = 0`, and thus `max/min z = e_1 * a_1 + 0 *a_2 = e_1*a_1`

Additionally, since `e_1+e_2 > 0` holds, then it must follow that at least one of the pair is `1` (that is, we must do either action exactly once).

Now that we have a way to model election, we can say that our objective function for day 1 shall be:

```C
base_souls                                                          +
lothric_1  * souls_lothric(total_str_1, total_dex_1, total_item_1)  +
londo_1    * souls_londo(total_str_1, total_dex_1, total_item_1)    +
archives_1 * souls_archives(total_str_1, total_dex_1, total_item_1) -
level_up(total_levels_1,0)
```

Subject to:

```C
lothric_1 * londo_1    = 0 {
lothric_1 * archives_1 = 0 { At most 1 of the 3 locations can be chosen
londo_1   * archives_1 = 0 {
lothric_1 + londo_1 + archives_1 = 1 <- At least 1 location must be chosen
base_souls - level_up(total_levels_1,0) >= 0 <- cannot go into debt
```

(In practice, since solvers use relaxation methods, and floating point arithmetic isn't precise around 0, we *must* relax the constraints: `lothric_1 * londo_1    = 0 => lothric_1 * londo_1    <= 1`, more about this in the How I Stopped Worrying section)

## Data declaration (Optional Read):

Let's introduce some notation for convinience

* `str_i : Int` -> Number of `strength` points earned in the run  `i`
* `dex_i : Int`  ->  Number of `dexterity` points earned in the run `i`
* `item_i : Int` ->  Number of `item discovery` points earned in the run `i`
* `lotrhic_i : Int` -> Discrete value (0 | 1) stating whether or not we visited `lothric` on day `i` 
* `londo_i : Int` -> Discrete value (0 | 1) stating whether or not we visited `londo` on day `i`
* `archives_i : Int` -> Discrete value (0 | 1) stating whether or not we visited `archives` on day `i`



## Objective Function And Restrictions per run

### Run 1

For the first run, the objective function would

```haskell
f_1 =
    base_souls_0                                                        +
    lothric_1 * souls_lothric(total_str_1, total_dex_1, total_item_1)   +
    londo_1 * souls_londo(total_str_1, total_dex_1, total_item_1)       +
    archives_1 * souls_archives(total_str_1, total_dex_1, total_item_1) -
    level_up(total_levels_1,0)
```
Subject to:

* `lotrhic_1*londo_1 = 0` - Cannot visit lothric and londo at the same time
* `lotrhic_1*archives_1 = 0` - Cannot visit lothric and archives at the same time
* `londo_1*archives_1 = 0` - Cannot visit londo and archives at the same time
* `total_levels_1 = str_1 + dex_1 + item_1` - Just for verbosity
* `base_souls_0 - level_up(total_levels_0) >= 0` - Cannot go into debt
* `total_str_1 = base_str + str_1` - Useful for run 2
* `total_dex_1 = base_dex + dex_1` - Useful for run 2
* `total_item_1 = base_item + item_1` - Useful for run 2

### Run 2


For the second run, the objective function would

```haskell
f_2 =
    f_1                                                                 +
    lothric_2 * souls_lothric(total_str_2, total_dex_2, total_item_2)   +
    londo_2 * souls_londo(total_str_2, total_dex_2, total_item_2)       +
    archives_2 * souls_archives(total_str_2, total_dex_2, total_item_2) -
    level_up(total_levels_2)
```

Subject to:

* `Restricciones 1` - Restrictions for the run 1
* `lotrhic_2*londo_2 = 0` -  Cannot visit lothric and londo at the same time
* `lotrhic_2*archives_2 = 0` -  Cannot visit lothric and archives at the same time
* `londo_2*archives_2 = 0` -  Cannot visit londo and archives at the same time
* `new_levels = str_2 + dex_2 + item_2`
* `total_levels_2 = total_levels_1 + new_levels` -  Just for verbosity
* `f_1 - level_up(new_levels,total_levels_2) >= 0` - No se permite endeudarse para subir de nivel.
* `total_str_2 = total_str_1 + str_2` -  Useful for run 3
* `total_dex_2 = total_str_1 + dex_2` -  Useful for run 3
* `total_item_2 = total_str_1+ item_2` -  Useful for run 3


### Run n

For the `n-th` run, the objective function would


```haskell
f_n =
    f_(n-1)                                                             +
    lothric_n * souls_lothric(total_str_n, total_dex_n, total_item_n)   +
    londo_n * souls_londo(total_str_n, total_dex_n, total_item_n)       +
    archives_n * souls_archives(total_str_n, total_dex_n, total_item_n) -
    level_up(new_levels,total_levels_(n-1))
```

Subject to:

* `Restricciones (n-1)` - Restrictions for the run `(n-1)`
* `lotrhic_n*londo_n = 0` -  Cannot visit lothric and londo at the same time
* `lotrhic_n*archives_n = 0` -  Cannot visit lothric and archives at the same time
* `londo_n*archives_n = 0` -  Cannot visit londo and archives at the same time
* `new_levels = str_n + dex_n + item_n` - Just for verbosity
* `total_levels_n = total_levels_(n-1) + new_levels` -  Just for verbosity
* `f_(n-1) - level_up(new_levels,total_levels_(n-1)) >= 0` -Cannot go into debt.
* `total_str_n = total_str_(n-1) + str_n` -  Useful for run `n+1`
* `total_dex_n = total_dex_(n-1) + dex_n` -  Useful for run `n+1`
* `total_item_n = total_item_(n-1)+ item_n` -  Useful for run `n+1`

## How I Stopped Worrying and Love the (1-)Linearity (Optional).

--Before continuing on: we define the term $n-$linearity as the number of variables in which a function is linear, i.e: $f(x,y)=x*y$ is $1-$ linear since $f(x+h,y) = f(x,y) + f(h,y)$, but it isn't 2-linear since: $f(x+h,y+h') \not = f(x,y) + f(h,h')$ --

After comming this far, you are surely asking yourself: is this problem... linear? 

The answer to that question is: it's complicated. Let us explain:

Our function is a polynomial of degree 1, so in that aspect it has _some_ linearity (at least 1-linear), nevertheless, there are 2 big obstacles on making it $n$-linear:

1.- There are some factors that depend on one another, i.e: `lotrhic_n * souls_lothric(str,dex,item)`

2.- **All** variables are **discrete**, i.e: `str` can only be a natural number, and `lotrhic_n` can obly be either 0 or 1.

Let's tackle (2) for the moment. 

So, let us say that $f$ is our objective function, whose domain is $\mathbb{N}^m$ for some natural number $m$, as of now, the Simplex algorithm can only work with continious functions, we cannot feed it the $f$ as it is... BUT (and it's a big but), let us _relax_ the discrete condition, that is, let us consider: $f'=f$ whose domain is: $\mathbb{R}^m$, that is, the "same" function, but extending the domain from the naturals to the reals, it turns out that **any** optimal value in $f'$ is (up to a $\pm 1$ error) also an optimal value in $f$ if we take the floor of its arguments, we shall call this: the _relaxation of $f$_.

Thus, by taking the _relaxation_ of our problem we can turn it into a form that Simplex can work with.

Now, after we _relax_ our function, we inmidiately loose $n-$linearity due to the fact that $x*y$ is not $n-$linear, therefore Simplex can't really handle our problem...

YET, this doesn't mean that our function isn't linear on some subspace of $\mathbb{R}^m$, if the solution lies in a linear neighboorhood, then we can take that linear neighboor as the true domain to our simplex algorithm, better yet, we can affirm that there exists such a neighboor since first degree polynomials are at least $1-$linear (it's a fun lil inductive exercise over the number of arguments!).

Thus the real question is: does the optimal solution lies within such a neighborhood? And to that we say: who really knows?

## Ok, but HOW on earth did you solve it? (Optional)

We used a combination of python to generate the function, variables and restrictions, and excels solver to find the solution. Nevertheless, excel can't really determine if the solution lies within a linear neighborhood (maybe because it's necessary to know the solution before hand?), thus we ended up using the Generalized Reduced Gradient (since we know that polynomials are smooth) to find the solution. The specficics on how python generates the solution and how does the excel sheet look like can be found in the source files.

Nevertheless, we are certain of something: that the grow of the optimal values (see graph below) evolve in a quasi-linear fashion, so if the trend holds for large $n$, we have a fine way to approximate the solution.

![Objective Function evolution](./imgs/Max_progression.png)


## About source (Optional).

It suffices to install the dependencies in the `requirements.txt` using `pip` to be able to run the suite. In order to generate new `.csv` files it suffices to run:

```bash
$ python generator.py
```

In order to generate samples from `1-8` runs, or:

```bash
$ python souls.py [n]
```

Where `n` is an integer representing the total number of runs that are allowed, if left empty, the default is 3, a more concrete example would be:


```bash
$ python souls.py 8
```