
// 大乐透/双色球
(function(window){
	// 复式计算
	var $ = window.jQuery,
		lottery = window.lottery,
		navBtn = $("#inner_nav").find("li"),
		navPage = $("#inner_box").find("div.jsq_tab_con"),
		boxFirst = $("#box_first"),
		boxSecond = $("#box_second"),
		btnsFirst = boxFirst.find("a"),
		btnsSecond = boxSecond.find("a"),
		btns = btnsFirst.add(btnsSecond),
		codes = $("#checked_codes"),
		nums = $("#checked_nums"),
		money = $("#checked_money"),
		nums2 = $("#checked_nums_2,#result_nums"),
		money2 = $("#checked_money_2,#result_money"),
		clear = $("#btn_clear"),
		input = $("#checked_text"),
		btnSet = $("#btn_set"),
		ckZjtz = $("#ck_zjtz"),
		first = [],
		second = [],
		fName = "前区",
		bName = "后区",
		fNum = 5,
		bNum = 2,
		fMax = 35,
		bMax = 12,
		winners = [
			[[5, 2]],
			[[5, 1]],
			[[5, 0]],
            [[4, 2]],
			[[4, 1]],
            [[3, 2]],
			[[4, 0]],
            [[3, 1], [2, 2]],
			[[3, 0], [1, 2], [2, 1], [0, 2]]
		],
		winningsList = [
			"A",
			"B",
			10000,
			3000,
			300,
			200,
            100,
            15,
            5
		];

	if (lottery == "ssq") {
		fName = "红球";
		bName = "蓝球";
		fNum = 6;
		bNum = 1;
		fMax = 33;
		bMax = 16;
		winners = [
			[[6, 1]],
			[[6, 0]],
			[[5, 1]],
			[[5, 0], [4, 1]],
			[[4, 0], [3, 1]],
			[[2, 1], [1, 1], [0, 1]]
		];
		winningsList = [
			"A",
			"B",
			3000,
			200,
			10,
			5
		];
	}

	// 导航切换
	navBtn.each(function(i){
		var btn = navBtn.eq(i);
		btn.click(function(){
			navBtn.removeClass("hover");
			btn.addClass("hover");
			navPage.hide().eq(i).show();
		});
	});

	// 排列组合
	function combine(m, n) {
		if (m < n || n<0) {
			return 0;
		}
		return factorial(m, m - n + 1) / factorial(n, 1);
	}

	// 阶乘
	function factorial(max, min) {
		if (max >= min && max > 1) {
			return max * factorial(max - 1, min);
		} else {
			return 1;
		}
	}

	// 开始计算
	function solve() {
		first = [];
		second = [];
		btnsFirst.filter(".selected").each(function(){
			first.push($(this).html());
		});
		btnsSecond.filter(".selected").each(function(){
			second.push($(this).html());
		});
		calculate();
	}

	// 计算并显示
	function calculate() {
		codes.html(first.join(" ") + " | " + second.join(" "));
		var ratio = 2,
			count = combine(first.length, fNum) * combine(second.length, bNum);
		if (ckZjtz.length && ckZjtz.attr("checked")) {
			ratio = 3;
		}
		nums.html(count);
		money.html((count * ratio).toString(10).replace(/(\d)(?=(\d{3})+($|\.))/g, '$1,') + " 元");
	}

	// 按钮点击
	btns.click(function(){
		$(this).toggleClass("selected");
		solve();
	});
	ckZjtz.click(calculate);
	clear.click(function(){
		btns.removeClass("selected");
		first = [];
		second = [];
		calculate();
	});
	btnSet.click(function(){
		var codes = $.trim(input.val()).replace(/[^\d\|]+/g, " ").split("|");
		if (codes.length > 2 || codes[0] == "") {
			alert("您输入的数据格式有误");
			return;
		}
		var f = codes[0],
			s = codes[1] || "";
		btnsFirst.each(function(){
			var btn = $(this);
			btn.toggleClass("selected", f.indexOf(btn.html()) != -1);
		});
		btnsSecond.each(function(){
			var btn = $(this);
			btn.toggleClass("selected", s.indexOf(btn.html()) != -1);
		});
		solve();
	});

	// 奖金计算
	var table = $("#main_table"),
		ckForeRequired = $("#ck_fore_required"),
		ckBackRequired = $("#ck_back_required"),
		spFore = $("#sp_fore"),
		spBack = $("#sp_back"),
		spForeRequired = $("#sp_fore_required"),
		spForeOptional = $("#sp_fore_optional"),
		spBackRequired = $("#sp_back_required"),
		spBackOptional = $("#sp_back_optional"),
		hitFore = $("#hit_fore"),
		hitBack = $("#hit_back"),
		hitForeRequired = $("#hit_fore_required"),
		hitForeOptional = $("#hit_fore_optional"),
		hitBackRequired = $("#hit_back_required"),
		hitBackOptional = $("#hit_back_optional"),
		fores = spForeRequired.add(spForeOptional).add(hitForeRequired).add(hitForeOptional),
		backs = spBackRequired.add(spBackOptional).add(hitBackRequired).add(hitBackOptional),
		checkedFR = false,
		checkedBR = false,
		cells = $("#row_result").find("td"),
		btnCalculate = $("#btn_calculate"),
		inputs = table.find("input.jsq_text"),
		winnings = $("#result_winnings"),
		fReq = 0,       // 前胆
		fOpt = 0,       // 前拖
		bReq = 0,       // 后胆
		bOpt = 0,       // 后拖
		fReqHit = 0,    // 前胆中
		fOptHit = 0,    // 前拖中
		bReqHit = 0,    // 后胆中
		bOptHit = 0;    // 后拖中

	// 设置胆拖切换
	function setCheck() {
		fores.toggle(checkedFR);
		backs.toggle(checkedBR);
		spFore.add(hitFore).toggle(! checkedFR);
		spBack.add(hitBack).toggle(! checkedBR);
	}

	// 计算投注数
	function bet(error) {
		fReq = 0,       // 前胆
		fOpt = 0,       // 前拖
		bReq = 0,       // 后胆
		bOpt = 0,       // 后拖
		if (checkedFR) {
			fReq = + spForeRequired.find("input").val();
			fOpt = + spForeOptional.find("input").val();
		} else {
			fOpt = + spFore.find("input").val();
		}
		if (checkedBR) {
			bReq = + spBackRequired.find("input").val();
			bOpt = + spBackOptional.find("input").val();
		} else {
			bOpt = + spBack.find("input").val();
		}
		if (error === true) {
			if (fReq > fNum) {
				alert(fName + "胆码最多选择" + fNum + "个号码");
				return;
			}
			if (bReq > bNum) {
				alert(bName + "胆码最多选择" + bNum + "个号码");
				return;
			}
			var fCount = fReq + fOpt,
				bCount = bReq + bOpt;
			if (fCount > fMax) {
				alert(fName + "号码数量不能超过" + fMax + "个");
				return;
			}
			if (bCount > bMax) {
				alert(bName + "号码数量不能超过" + bMax + "个");
				return;
			}
			if (fCount < fNum) {
				alert(fName + "号码数量应不少于" + fNum + "个");
				return;
			}
			if (bCount < bNum) {
				alert(bName + "号码数量应不少于" + bNum + "个");
				return;
			}
		}
		var count = combine(fOpt, fNum - fReq) * combine(bOpt, bNum - bReq);
		nums2.html(count);
		money2.html((count * 2).toString(10).replace(/(\d)(?=(\d{3})+($|\.))/g, '$1,'));
		return true;
	}

	// 开始奖金计算
	function hit() {
		if (! bet(true)) {
			return;
		}
        fReqHit = 0,    // 前胆中
		fOptHit = 0,    // 前拖中
		bReqHit = 0,    // 后胆中
		bOptHit = 0;    // 后拖中
		if (checkedFR) {
			fReqHit = + hitForeRequired.find("input").val();
			fOptHit = + hitForeOptional.find("input").val();
		} else {
			fOptHit = + hitFore.find("input").val();
		}
		if (checkedBR) {
			bReqHit = + hitBackRequired.find("input").val();
			bOptHit = + hitBackOptional.find("input").val();
		} else {
			bOptHit = + hitBack.find("input").val();
		}
		if (fReqHit > fReq) {
			alert(fName + "命中个数应少于选择的" + fName + "号码个数");
			return;
		}
		if (bReqHit > bReq) {
			alert(bName + "命中个数应少于选择的" + bName + "号码个数");
			return;
		}
		if (fReqHit + fOptHit > fNum) {
			alert(fName + "命中个数应少于" + fNum + "个");
			return;
		}
		if (bReqHit + bOptHit > bNum) {
			alert(bName + "命中个数应少于" + bNum + "个");
			return;
		}
		win();
	}

	// 计算前区或后区命中指定个数的方案注数
	function solveHits(num, req, opt, reqHit, optHit) {
		var optLeft = num - req,
			optMiss = opt - optHit,
			max = reqHit + optHit,
			hits = [];
		for (var i = 0; i <= num; ++ i) {
			if (i < reqHit || i > max) {
				hits[i] = 0;
			} else {
				var optNeed = i - reqHit;
				hits[i] = combine(optHit, optNeed) * combine(optMiss, optLeft - optNeed);
			}
		}
		return hits;
	}

	// 计算各奖项命中的方案注数
	function win() {
//	    fHits: 前区命中个数， bHits: 后区命中个数
//	    fNum: 前区开奖个数， bNum: 后区开奖个数
		var fHits = solveHits(fNum, fReq, fOpt, fReqHit, fOptHit),
			bHits = solveHits(bNum, bReq, bOpt, bReqHit, bOptHit),
			result = [];
		for (var i = 0; i < winners.length; ++ i) {
			var winner = winners[i],
				count = 0;
			for (var j = 0; j < winner.length; ++ j) {
				var item = winner[j];
				count += fHits[item[0]] * bHits[item[1]];
			}
			result[i] = count;
		}
		display(result);
	}

	// 显示结果
	function display(result) {
		var strs = [],
			total = 0,
			index = 4;
		if (lottery == "dlt") {
			cells.eq(0).html(fReqHit || "-");
			cells.eq(1).html(fOptHit || "-");
			cells.eq(2).html(bReqHit || "-");
			cells.eq(3).html(bOptHit || "-");
		} else {
			index = 3;
			cells.eq(0).html(fReqHit || "-");
			cells.eq(1).html(fOptHit || "-");
			cells.eq(2).html(bOptHit || "-");
		}
		cells.slice(index, index + result.length).each(function(i){
			var count = result[i];
			$(this).html(count);
			if (count > 0) {
				var value = winningsList[i];
				if (typeof value == "string") {
					strs.push((count == 1 ? "" : count + "*") + value);
				} else {
					total += count * value;
				}
			}
		});

		if (total > 0) {
			strs.push(total);
		}
		var str = strs.join(" + ") || "0";
		winnings.html(str);
		cells.last().html('<span class="red">' + str + "</span>元");
	}

	ckForeRequired.click(function(){
		checkedFR = this.checked;
		setCheck();
	});
	ckBackRequired.click(function(){
		checkedBR = this.checked;
		setCheck();
	});
	btnCalculate.click(hit);
	inputs.keyup(bet).blur(bet);

})(window);
