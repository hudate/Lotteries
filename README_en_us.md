# Lotteries
**彩票项目：** 大乐透和双色球

## How to use?
**Please run it with root. Caused by the program will kill some dirs and files at /tmp.**

First: You **must** confirm the project at your HOME DIR, just like "C:/Users/xxx in windows" or "/home/xxx" on linux or mac os and other unix system.

Second: There is a Function named "start()" in start.py, you can run it by "python3 start.py". But you should input a **string** with sender and a **mailing list** when you first run it.

## How to set mail_setup.json?
You should set the file "$HOME_DIR/Lotteries/tools/mail_setup.json". Your have two methods to setting the file:
    
    1. before run it
    copy file "$HOME_DIR/Lotteries/tools/mail_setup.json" and rename "$HOME_DIR/Lotteries/tools/mail_setup.json".
    add sender and mail list in "$HOME_DIR/Lotteries/tools/mail_setup.json".
    
    2. after run it
    


## 后期补充实现
1. 分区对每期每个专家的预测做正确率统计，并存入数据库； [ v ]
2. 分区按照最近的（50期， 30期， 20期， 10期， 9 8 7 6 5）对专家进行排名； [ v ]
3. 分区每个分期分别对排名前5~20名专家，进行本期预测的正确率统计（前区个数：[开奖球数 + 1， 开奖球数 + 3], 后区：[开奖球数 + 1， 开奖球数 + 3]）； [ v]
4. 对计算得到的数据，进行准确率筛选，找到合适的参数 [  ]   暂时使用一组定量代替。
5. 上两步之后，应该会得出一个正确率的模型（包括预测期数，每期预测的专家个数，杀球个数，买球个数）  -> 汇总入库； [ x ]      依赖于上一步
6. 按照分析的专家结果和期数，获取当期的预测数据，进行分析预测（看球在专家预测中出现的次数大小，并使用杀球去过滤，然后按出现次数排名）； [ v ]
7. 目标：8+4 （对3+2或者4+1）； [ x ]      有待检验
8. 中奖率和收益率分析。   [  ]      有待实现
9. 可能还需要实现代理池。 [  ]      视情况而定
10. 移除/tmp目录下，由于使用geckodriver产生的一些文件，主要是：/tmp/tmpxxxxxxx 和 /tmp/rust_xxxxx目录。        [ v ]

1.减少“空跑”等待时间到5分钟，确保一旦因为bug停止，5分钟可以拉起程序，但是如果正常，依然是半小[ ]
2.增加某一期预测数据获取[ ]
3.某一期预测准确率[v]
4.对爬虫进行改进(暂时没有想法)
5.增加对于某一期实现不同的参数预测(例如：多个期数，多个专家数)，并选出最佳的参数(1.使用传统的均值+标差排名，取最好的一组；2.找人用智能算法找参数：粒子群最优解，xgboost等)
6.对数据增加改进：对每期的每个专家增加article_list键，用于保存截止当期该专家的预测文章数量，以供5进行判断预测专家时使用。对于爬取的专家数量也该改进到爬取60个。
7.想办法，对于第一次运行时，把所有的数据快速爬取下来，可能有十几万条数据60(60*4*70)