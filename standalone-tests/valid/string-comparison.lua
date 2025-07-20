
static_assert("a" < "z")
static_assert("z" <= "z")
static_assert("a" <= "z")
static_assert("z" > "a")
static_assert("z" >= "a")
static_assert("z" >= "z")

static_assert(not("a" > "z"))
static_assert(not("a" >= "z"))
static_assert(not("z" < "a"))
static_assert(not("z" <= "a"))

