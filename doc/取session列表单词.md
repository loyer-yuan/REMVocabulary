# 取session列表单词

## 为study单词

### 更新remember_word的study_number+1

### 首先给出全英的单词，和例句

- 熟悉，直接在列表中删除单词，并且在temp_book删除，并更新word_book为finished
- 模糊

	- 放在列表最后面，然后更改为repeat，并且更新temp_book中单词的list值为2，degree为preview2

- 陌生

	- 放在列表最后面，然后更改为repeat，并且更新temp_book中单词的list值为1，degree为preview1

## 为preview1\preview2

### 首先给出测试的单词, 需要单词的拼写

- 如果点击熟悉，直接在列表中删除单词，并且在temp_book删除，并更新word_book为高一级（这里包括了not_learning)
- 如果不成功拼写单词，则继续拼写
- 如果成功拼写单词，则跳转到给出详细单词的页面，并且，让用户选择熟悉、模糊，陌生

	- 熟悉

		- 如果原本是preview2，则在列表中删除单词，并且在temp_book删除，并更新word_book为高一级，oblivion的remember_number+1
		- 如果原本是preview1，则在列表中删除单词，在temp_book中更改为preview2，设置degree为2

	- 模糊、陌生

		- 放在列表最后面，然后更改为session列表该单词为repeat，设置temp_book的list为1，degree为preview1
		- 模糊

			- 如果word_book的degree原本为f系列，下降一个等级，直到f1。能下降的话，oblivion的forget_number+1

		- 陌生

			- 如果word_book的degree原本为f系列，直接到f1。oblivion的forget_number+1

		- oblivion的forget_number+1

- 回到最初的选择

## repeat

### 首先给出测试的单词, 需要单词的拼写

- 如果点击熟悉，直接在列表中删除单词
- 如果不成功拼写单词，则继续拼写
- 如果成功拼写单词，则跳转到给出详细单词的页面，并且，让用户选择熟悉、模糊，陌生：

	- 如果点击模糊、陌生，继续放在列表后面

## 重新抽取

## 显示单词详细信息
