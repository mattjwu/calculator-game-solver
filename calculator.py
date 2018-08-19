class Button:
	def __init__(self, *args):
		self.val = None
		if len(args) == 1:
			self.val = args[0]

	def push(self, num, turn):
		return num

	def upkeep(self, num, turn):
		pass

	def get_rep(self, idx):
		name = self._get_class_name()
		if hasattr(self, 'val') and self.val:
			return name + '({})'.format(self.val)
		return name

	def _get_class_name(self):
		s = str(self)
		return s[10:s.index('object') - 1]

	def handle_used(self, turn):
		pass

	def reset(self, num, turn):
		pass

class Add(Button):
	def push(self, num, turn):
		return self.val + num

class Append(Button):
	def push(self, num, turn):
		return int(str(num) + str(self.val))

class Inv(Button):
	def push(self, num, turn):
		s = str(num)
		n = [str((10 - int(digit)) % 10) for digit in s]
		return int(''.join(n))

class Left(Button):
	def push(self, num, turn):
		if len(str(num)) == 1:
			return [0]
		return int(str(num)[:-1])

class Mirror(Button):
	def push(self, num, turn):
		return int(str(num) + str(num)[::-1])

class Multiply(Button):
	def push(self, num, turn):
		return num * self.val

class Replace(Button):
	def __init__(self, *args):
		self.old = args[0]
		self.new = args[1]

	def push(self, num, turn):
		return int(str(num).replace(str(self.old), str(self.new)))

class Reverse(Button):
	def push(self, num, turn):
		return int(str(num)[::-1])

class Shift(Button):
	def push(self, num, turn):
		if self.val == 'r':
			return int(str(num)[-1:] + str(num)[:-1])
		elif self.val == 'l':
			return int(str(num)[1:] + str(num)[:1])

class Store(Button):
	def __init__(self):
		self.possible = []
		self.pushes = []

	# TODO: I think that I'm missing the number that you push
	# e.g. I think if you have 1, 2, 3, and on turn 4 you use 2
	# then it won't keep track of you still being allowed to use 2
	# but it will correctly ignore 1 and 3 i'm not sure too much brain
	def push(self, num, turn):
		lst = [
			int(str(num) + str(poss_num))
			for poss_num in self.possible[self._get_push_index():]
		]
		self.pushes.append(turn)
		return lst

	def upkeep(self, num, turn):
		self.possible[turn:] = []
		self.possible.append(num)
		self.pushes = list(filter(
			lambda x: x < turn, self.pushes
		))

	def reset(self, num, turn):
		self.possible[turn:] = []
		self.possible.append(num)
		self.pushes = list(filter(
			lambda x: x < turn, self.pushes
		))

	def get_rep(self, idx):
		prefix = super().get_rep(idx)
		return prefix + '({})'.format(self.possible[self._get_push_index():][idx])

	def _get_push_index(self):
		push_index = 0
		if self.pushes:
			push_index = self.pushes[-1]
		return push_index

class Sub(Add):
	def __init__(self, *args):
		super().__init__(args)
		self.val = -self.val


class Problem:
	def __init__(self, initial, goal, max_turns, buttons, portal=None):
		self.initial = initial
		self.goal = goal
		self.max_turns = max_turns
		self.buttons = buttons
		self.portal = portal

	def solve(self):
		return self._solve(self.initial, 0)

	def _solve(self, num, turn):
		if num == self.goal:
			return []

		if turn == self.max_turns:
			return None

		for _button in self.buttons:
			_button.upkeep(num, turn)

		for button in self.buttons:
			new_nums = button.push(num, turn)
			if type(new_nums) != list:
				new_nums = [new_nums]
			if self.portal:
				new_nums = [
					self._handle_portal(num)
					for num in new_nums
				]

			explored = set()
			for idx, new_num in enumerate(new_nums):
				if (new_num in explored) or (new_num == num):
					continue
				explored.add(new_num)

				rest_soln = self._solve(new_num, turn + 1)
				for _button in self.buttons:
					_button.reset(num, turn)
				if rest_soln is not None:
					return [
						num, button.get_rep(idx)
					] + rest_soln

	def _handle_portal(self, num):
		entrance, exit = self.portal
		if len(str(num)) < entrance:
			return num

		rest_num = int(str(num)[:-entrance] + str(num)[1 - entrance:])
		pulled = int(str(num)[-entrance:1 - entrance])

		new_num = rest_num + pulled * 10 ** (exit - 1)

		return self._handle_portal(new_num)


p = Problem(189, 500, 6,
	[
		Add(8),
		Multiply(4),
		Inv(),
		Append(9),
		Replace(7, 0)
	],
	[4, 1]
)
print(p.solve())
