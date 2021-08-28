# 项目逻辑设计
## 用户模块
对于注册、和注销用户，只需要用一个用户表维持数据就行。对于登录和退出登录来说，只需要查用户表即可
1. user (<u>账户名</u>， 别名， 密码， 注册时间)
   * 增：注册用户
   * 删：注销用户
   * 改：修改密码，修改用户名
   * 查：登录用户
2. Remember-word (<u>账户名</u>， 规划每天记忆的单词数量, 学习的单词总量， 复习的单词总量)
**注：每次从not learning学习完，学习的单词总量+1；每次复习完（从f1...f15），复习的次数+1**
3. check-in-form (<u>id</u>，<u>账户名</u>，连续签到次数， 最近签到时间)
**~~注：登录一次就签到一次：签到时：检查id最大的记录的最近签到时间是否为昨天，是的话，更新签到时间，并且，连续签到次数+1；
如果不是，增加一条记录，并且id数+1.~~**


## 单词模块
1. vocabulary (<u>单词</u>， <u>词性</u>， 中文解释)
2. Example (<u>例句</u>， 单词, 中文翻译)
3. pronounce (<u>单词</u>， <u>口音</u>， 音频存放的url)
4. not_found(<u>单词</u>) 注：存放找不到的单词

## 记忆模块
1. word-book (<u>单词</u>， <u>单词本</u>， <u>账户名</u>， 记忆程度（not learning， unfamiliar，blur， f1, f2, f4, f7, f15, finished）， 最后更新时间)
2. temp-book (<u>单词</u>， <u>单词本</u>， <u>账户名</u>)

**每次从数据库取当天要背的单词时，先取出未学习（not learning）的单词，检查是否达到当天学习的数量。
如果超出，则截取前面的部分出来。如果不够，继续取到时间复习的陌生的单词；
依次这样按顺序取到时间复习的不同程度单词，最后再取要学习的单词。**

- **陌生、模糊单词的复习时间：当天**
- **其他熟悉的单词，按照f后面的数字来决定天数，如：f1，也就是1天后复习**
- **如果到时间还没有时间复习（超出了每天规划的记忆单词数量），则打上not learning标记**

### 记忆单词：
**首先，判断有没有初次学习的单词：**
- **有：则开始初次学习。如果是陌生，则这一轮学习立刻复习，如果是模糊，则下一轮再复习；如果熟悉，则今天不用复习，直接进入f1状态。**
- **无：开始复习**
   - **复习的时候如果选择了陌生和模糊，还是按照和学习一样的策略。（可以理解，毕竟是学习，还没到复习的阶段）**
   - **如果选了熟悉，则要复习两边，熟悉1和熟悉2。熟悉1，放在下一轮复习，熟悉2，放在下2轮。**
   - **如果到了最后一轮，则如果点击熟悉，则直接录入数据库，在原有的等级上升1级，比如从f1，如果再次熟悉，就到f2。**
**如果，点击陌生和模糊，直接录入数据库。**

## 数据展示模块
- oblivion（<u>账户名</u>， 遗忘单词次数, 记忆单词的次数）
**注：是原本f系列，但之后变成模糊和陌生。
注：出现一次f1，增加一次**
- oblivion-rate (<u>账户名</u>， <u>日期</u>， 遗忘率)
**~~注：登录一次计算一次~~**

## 特殊模块
**直接导入单词本，或者导出单词本**