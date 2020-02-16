# 彩票
## 项目说明
**项目目的:** 使用其他专家的数据，研究预测待开奖期的结果，并可以将其发送给邮件列表中的收件人。 \
**主要功能:**
  1. 爬取彩经网上四个区域（前区预测，前区杀球，后区预测，后区杀球）将开奖期的专家列表（这个是有排序的）
  2. 对这些专家的预测数据爬取
  3. 对四个区的专家分别进行准确率排名（按照往期的平均准确率和标准差进行排名），分别取前N个专家
  4. 爬取3中每个专家的预测数据，并进行汇总（计算每个球在所有专家预测数据中出现的次数，并按照需要的个数来取出排名前M个杀球，再从预测球中排除杀球，再对剩余的预测球排序，取出排名靠前的前L个预测球）
  5. 对4中得到的球进行正确率分析和固定投入计算
  6. 发送邮件
  7. 数据库数据清理
 
**彩票名称：** 福彩双色球，体彩大乐透 \
**后续改进：** 持续改造中，参考”后续改进“ \
**长期计划：** 
    1. 加入对”体育彩票：竞彩“的分析      [  ]

## 目录结构
```tree
/home/xxx/Lotteries
.
├── dataB           # 获取之前的数据，主要是获取往期的开奖数据
│   ├── auto_begin.py
│   ├── get_lotteries_data.py
│   ├── __init__.py
│   ├── options.yaml
│   └── read_options.py
├── dataP           # 和预测数据有关的操作
│   ├── auto_begin.py
│   ├── auto_get_experts.py
│   ├── auto_get_predict_data.py
│   ├── auto_get_predict_data_urls.py
│   ├── geckodriver.log
│   ├── get_now_stage_expert_predict_data_with_browser.py
│   ├── get_now_stage_expert_predict_data_without_browser.py
│   ├── get_now_stage_experts_predict_data.py
│   ├── __init__.py
│   ├── options.yaml
│   ├── read_options.py
│   └── set_referer.py
├── log             # 记录日志
│   └── lotteries.log
├── proxy           # 获取代理
│   ├── check_proxy.py
│   ├── clear_proxies.py
│   ├── get_proxy.py
│   ├── __init__.py
│   ├── save_proxy.py
│   ├── settings.py
│   └── ua.py
├── README_en_us.md
├── README.md
├── record      # 保存着每天的预测数据
│   └── 2020-01-09_ssq_2020004.txt
├── requirements.txt
├── settings.py # 一些设置，后续将会把某些设置写入到setup.json中去
├── start.py    # 入口
├── setup.json    # 全局设置
├── setup_tmplate.json    # 全局设置模板，用于第一次运行时的部分设置
├── throw       # 本来用于扔掉的部分
│   ├── analyse_data_test.py
│   ├── auto_analyse_data_old2.py
│   ├── auto_analyse_data_old.py
│   ├── auto_analyse_data_test.py
│   ├── auto_get_experts_old.py
│   ├── dataB_manul_begin.py
│   ├── delete_vars.py
│   ├── get_caibi.py
│   ├── get_cookies.py
│   ├── get_experts.py
│   ├── get_predict_data.py
│   ├── get_predict_data_urls.py
│   ├── manual_analyse_data.py
│   ├── manul_begin.py
│   ├── new_analyse_data_test.py
│   ├── predict_data.py
│   ├── right_ratio.py
│   └── test付费.py
└── tools           # 主要的功能操作部分
    ├── auto_analyse_data.py
    ├── auto_check_articles_list.py
    ├── auto_compose_data.py
    ├── auto_get_kjxx.py
    ├── auto_predict_data.py
    ├── check_predict_data.py
    ├── common.py
    ├── compose_data.py
    ├── __init__.py
    ├── logger.py
    ├── save_data.py
    ├── send_mail.py
    ├── set_proxies.py
    └── ua.py
```

## 怎么使用？
**使用root用户运行，因为需要删除/tmp下的部分文件夹。**
  1. 确认安装了mongodb软件。
  2. 确认python安装了需要的包，可以直接使用”python绝对路径 -m pip install -r requirements.txt“
  3. 确认Lotteries项目位于$HOME_DIR下。windows系统：C:/Users/xxx文件夹下；linux， mac OS和其他unix系统：/home/xxx.
  4. 运行程序(此处可能会遇到需要设置邮件收发件人，参看如何修改收发件人？)： \
    i. 手动：使用“python3绝对路径 start.py”来启动程序 \
    ii. linux开机运行：编辑"/etc/rc.local"文件，然后把“python绝对路径 /home/xxx/Lotteries/start.py"写入，再给rc.local文件加上可执行权限即可。
  5. 如果需要真实预测使用，则需要（此处可能会遇到需要设置彩经网账户和密码，参看如何添加彩经网账户密码？）：    \
    i. 注册/使用“彩经网”账户；    \
    ii. 把注册得到的账户和密码填入init.json文件中。
 

## 如何修改收发件人？
方法一： 手动复制setup_template.json为setup.json，并且修改setup.json文件中mail中的sender，receivers和password的值。    \
方法二： 执行使用“python3绝对路径 start.py”，之后，输入一个字符串：sender和一个列表：收件人列表（必须输入"\[" 和 "\]"）。


## 如何添加彩经网账户密码？
方法一： 手动复制setup_template.json为init.json，并且修改setup.json文件中的lotteries中的account和password的值。   \
方法二： 执行使用“python3绝对路径 start.py”，之后，按提示输入。


## 后续改进
1. 减少“空跑”等待时间到5分钟，确保一旦因为bug停止，5分钟可以拉起程序，但是如果正常，依然是半小时。   [  ]    
2. 增加某一期预测数据获取。  [  ]    
3. 某一期预测准确率。 [  ]   
4. 对爬虫进行改进(暂时没有想法)   [  ]
5. 增加对于某一期实现不同的参数预测(例如：多个期数，多个专家数)，并选出最佳的参数： \
    i. 使用传统的均值+标差排名，取最好的一组  \
    ii. 找人用智能算法找参数：粒子群最优解，xgboost等  (暂时不知道哪种好)  [  ] 
6. 对数据增加改进：对每期的每个专家增加article_list键，用于保存截止当期该专家的预测文章数量，以供5进行判断预测专家时使用。对于爬取的专家数量也该改进到爬取60个。    [  ]    
7. 想办法，对于第一次运行时，把所有的数据快速爬取下来，可能有十几K数据（80 * 4 * 70）    [  ]


## 潜在威胁
1. 数据爬取：能不能按时爬取完所需要的数据          [  ]
2. 关于自己的专家排名，有无更科学的排名算法？        [  ]
3. 对于实际使用中，如何确保需要的数据成功爬取？尤其是需要登录付费的部分。      [  ]