class Button:
	def __init__(self, *args):
		self.val = None
		if len(args) == 1:
			self.val = args[0]

	def push(self, num, turn):
		return num

	def get_rep(self):
		name = self._get_class_name()
		if hasattr(self, 'val') and self.val:
			return name + '({})'.format(self.val)
		return name

	def _get_class_name(self):
		s = str(self)
		return s[10:s.index('object') - 1]


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
		self.used = None
		self.previous = []
		self.pushes = []

	def push(self, num, turn):
		lst = [
			[idx, int(str(num) + str(poss_num))]
			for idx, poss_num in self._get_possible()
		]
		self.pushes.append(turn)
		return lst

	def upkeep(self, num, turn):
		self.previous[turn:] = []
		self.previous.append(num)
		self.pushes = list(filter(
			lambda x: x < turn, self.pushes
		))

	def reset(self, num, turn):
		self.previous[turn:] = []
		self.previous.append(num)
		self.pushes = list(filter(
			lambda x: x < turn, self.pushes
		))

	def set_used(self, idx):
		self.used = idx

	def get_rep(self):
		prefix = super().get_rep()
		return prefix + '({})'.format(self.previous[self.used])

	def _get_possible(self):
		latest_push = self.pushes[-1] if self.pushes else -1
		last_used = None
		if self.used is not None:
			last_used = self.previous[self.used]
		possible = []
		if last_used:
			possible.append([self.used, self.previous[self.used]])
		for i in range(latest_push + 1, len(self.previous)):
			possible.append(
				[i, self.previous[i]]
			)
		return possible


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
		self.store = None
		for button in buttons:
			if isinstance(button, Store):
				self.store = button
				break

	def solve(self):
		return self._solve(self.initial, 0)

	def _solve(self, num, turn):
		if num == self.goal:
			return []

		if turn == self.max_turns:
			return None

		for button in self.buttons:
			self._update_store(num, turn)
			if button == self.store:
				saved_used = self.store.used
				new_num_pairs = self.store.push(num, turn)
				new_num_pairs = [
					[pair[0], self._handle_portal(pair[1])]
					for pair in new_num_pairs
				]
				explored = set()
				for idx, new_num in new_num_pairs:
					if (new_num in explored or new_num == num):
						continue
					explored.add(new_num)

					self.store.set_used(idx)
					rest_soln = self._solve(new_num, turn + 1)
					self._reset_store(num, turn)
					self.turn = turn
					if rest_soln is not None:
						this = [num, self.store.get_rep()]
						self.store.set_used(saved_used)
						return this + rest_soln
				self.store.set_used(saved_used)
				continue

			new_num = button.push(num, turn)
			new_num = self._handle_portal(new_num)

			if new_num == num:
				continue

			rest_soln = self._solve(new_num, turn + 1)
			self._reset_store(num, turn)

			if rest_soln is not None:
				return [
					num, button.get_rep()
				] + rest_soln

	def _update_store(self, num, turn):
		if self.store is None:
			return
		self.store.upkeep(num, turn)

	def _reset_store(self, num, turn):
		if self.store is None:
			return
		self.store.reset(num, turn)

	def _handle_portal(self, num):
		if self.portal is None:
			return num
		entrance, exit = self.portal
		if len(str(num)) < entrance:
			return num

		rest_num = int(str(num)[:-entrance] + str(num)[1 - entrance:])
		pulled = int(str(num)[-entrance:1 - entrance])

		new_num = rest_num + pulled * 10 ** (exit - 1)

		return self._handle_portal(new_num)


p = Problem(1, 12131412131, 6,
	[
		Store(),
		Append(2),
		Append(3),
		Append(4)
	],
)
print(p.solve())
