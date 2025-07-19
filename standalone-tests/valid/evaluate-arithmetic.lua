static_assert((12 * 12) == 144)
static_assert((12 + 12) == 24)

static_assert((12 - 12) == 0)
static_assert((12 / 6) == 2) 

static_assert(1 == 1)
static_assert(1 ~= 2)
static_assert(not (1 == 2))

static_assert(2 > 1)
static_assert(2 >= 1)
static_assert(2 >= 2)

static_assert(1 < 2)
static_assert(1 <= 2)
static_assert(2 <= 2)

static_assert(not(1 > 1))
static_assert(not(0 >= 1))

static_assert(not(2 < 2))
static_assert(not(2 <= 0))

