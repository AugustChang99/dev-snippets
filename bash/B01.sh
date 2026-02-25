#!/bin/sh

#################################################
# 功能簡述：用來處理geometry optimize(non ts)
# 版本：2024.04.05版
#################################################
#===================================================================
#【part1：判斷有沒有路徑底下有沒有default_setting_temp或user_setting_temp】
#因為後續會讓使用者可以自訂user_setting的內容，所以要先確認同路徑底下是否存有相關的temp檔。

#如果default_setting_temp、user_setting_temp都不存在，就生成一個default_setting_temp放在路徑下，並展示default setting的參數。
if [ ! -f "default_setting_temp" ] && [ ! -f "user_setting_temp" ]; then
    cat << END > default_setting_temp
%nprocshared=4
%mem=512MW
# b3lyp/cc-pVTZ opt freq

Title Card Required
END
    clear
    #預設為4CPU、512MW的記憶體，計算用的hybrid functional是b3lyp，basis set是cc-pVTZ。
    echo '================================='
    echo '【current setting(default setting)】'
    echo '  CPU：4'
    echo '  memory：512MW'
    echo '  hybrid functional：b3lyp'
    echo '  basis set：cc-pVTZ'
    echo '================================='
    echo
    echo
    read -p "按任意鍵繼續..."

#如果user_setting_temp存在，那就刪掉default_setting_temp，並展示user setting的參數。
elif [ -f "user_setting_temp" ]; then
    rm default_setting_temp
    clear

    #將user_setting_temp中的特定內容抓出來設為變數
    CPU=$(sed -n '1{s/%nprocshared=\(.*\)/\1/p;q;}' user_setting_temp)
    memory_setting=$(grep '%mem=' user_setting_temp | sed 's/%mem=//')

    line=$(sed -n '3p' user_setting_temp)
    hybrid_functional=$(echo "$line" | sed -n 's/.*# \([^\/]*\)\/\([^ ]*\).*/\1/p')
    basis_set=$(echo "$line" | sed -n 's/.*# \([^\/]*\)\/\([^ ]*\).*/\2/p')

    echo '================================='
    echo '【currrent setting(user setting)】'
    echo '  CPU：'$CPU
    echo '  memory：'$memory_setting
    echo '  hybrid functional：'$hybrid_functional
    echo '  basis set：'$basis_set
    echo '================================='
    echo
    echo
    read -p "按任意鍵繼續..."

#這邊的else應該只剩下default_setting_temp存在、user_setting_temp不存在的情況，這時候就展示default setting的參數。
else
    clear
    #預設為4CPU、512MW的記憶體，計算用的hybrid functional是b3lyp，basis set是cc-pVTZ。
    echo '================================='
    echo '【default setting】'
    echo '  CPU：4'
    echo '  memory：512MW'
    echo '  hybrid functional：b3lyp'
    echo '  basis set：cc-pVTZ'
    echo '================================='
    echo
    echo
    read -p "按任意鍵繼續..."
fi

#===================================================================
#【part2：功能選項】
#規劃提供五種功能供使用者使用。
#功能1：可讓使用者批量將gjf檔轉成com檔
#功能2：可讓使用者批量將log檔轉成com檔
#功能3：可讓使用者自行更改
    #功能3a：可將目前的設定還原回default設定
    #功能3b：可更改目前的設定為使用者自訂
#功能4：可讓使用者實現批量改名
#功能5：可讓使用者實現批量送job

echo
while :
do
    clear
    echo ============================================================================
    echo '【使用說明】'
    echo '1.本程式會將資料夾內的特定類型檔案統一轉檔，非轉檔目標請不要上傳到同路徑下。'
    echo '2.如果gjf檔中沒有Title Card Required的字樣，功能一會抓不到座標'
    echo '3.如果log檔中沒有Distance matrix的字樣，功能二會抓不到座標(如：氫分子)。'
    echo ============================================================================
    echo
    echo 'options:'
    echo
    echo '1) .gjf => .com (for non-ts)'
    echo
    echo '2) .log => .com (for non-ts)'
    echo
    echo '3) change setting & update'
    echo
    echo '4) chage file name' 
    echo
    echo '5) autosub'
    echo
    echo 'x) exit'
    echo
    echo -n 'which one? '
    read opt
    echo

    case "$opt" in
    1)
        #read -p 'Which method?(b3lyp, mp2, CCSD....)' method
        read -p 'How many atoms in your compound?=>' how_many_atoms
        read -p 'The Charge of this job is : neutral(\"0\") cation(\"1\") anion(\"-1\") ?=>' charge
        read -p 'The Multiplicity of this job is : Single(\"1\") Doublet(\"2\") Triplet(\"3\") ?=>' multiplicity

        ls -l *.gjf|awk '{ print $9 }' > temp.txt
        X=$(wc -l temp.txt | awk '{print $1}' )
        #將temp.txt的總行數列出並設為變數X，要用awk是因為wc -l也會把檔名列出來，因此只需要印出第一個位置的資料(即 總行數)
        Y=1
        while test $X == 0
        do
            echo
            echo '===================================================='
            echo
            echo '資料夾中沒有找到.gjf檔，請重新上傳.gjf檔到資料夾中'
            echo
            echo '===================================================='
            echo
            echo
            break
        done

        while test $Y -le $X
        #當變數Y小於X的情況下，就執行以下的do loop
        do
            name=$(sed -n "${Y}p" temp.txt|sed 's/.gjf//g')
            #將temp.txt檔中的第B行資料抓出來設為變數name
            
            grep_lines=$(expr $how_many_atoms + 3)
            #這邊要抓的行數是原子數+3行的行數(和gjf檔的固定格式有關)
            
            coordination=$(grep -A $grep_lines 'Title Card Required' $name.gjf|sed '1,3d')
            #sed '1,3d'的意思是把抓出來資料的前3行裁掉
            #這樣抓出的資料就只會有原子的座標(不含%、#、Title Card Required那幾行的其餘資料，和.gjf檔的固定格式有關)
            #接著把grep出來的資料當成變數，塞到新創建的.com中即可

            #經過part1的篩選後，同個路徑底下的setting檔，理論上只會剩default setting、user setting當中的其中一種。
            #不過為了以防萬一出了啥特殊bug，所以用elif撰寫，不使用else。
            if [ -f default_setting_temp ]; then
                setting=$(grep -A 6 '%nprocshared' default_setting_temp)
            elif [ -f user_setting_temp ]; then
                setting=$(grep -A 6 '%nprocshared' user_setting_temp)
            fi

            cat << END > $name.com
%chk=$name.chk
$setting

$charge $multiplicity
$coordination
END

            dos2unix $name.com #這行是用來處理掉系統造成的換行符號
            
            #vi $name.com #如果有需要改.com檔的內容，就把這行加上去，改完存完檔就能自動上傳了
            #~/mksh $name #如果需要直接將com檔拿去送，就補這行

            if grep -q "Title Card Required" $name.gjf; then
                echo -e "<> \e[1;32;40m$name.com\e[0m has done! "
                rm $name.gjf #如果需要刪掉原本上傳的gjf檔就補這行
            else
                echo -e "<> \033[31m$name.com\033[0m doesn't have coordination!!!!!!! "
            fi

            Y=$(expr $Y + 1)
            #執行完上述所有命令後將變數Y+1，這樣才能讓迴圈繼續下去。
        done
        rm temp.txt
        echo
        echo
        read -p "按任意鍵繼續..."
        ;;

    2)
        read -p 'The Charge of this job is : neutral(\"0\") cation(\"1\") anion(\"-1\") ?=>' charge
        read -p 'The Multiplicity of this job is : Single(\"1\") Doublet(\"2\") Triplet(\"3\") ?=>' multiplicity
        ls -l *.log|awk '{ print $9 }' > temp.txt
        X=$(wc -l temp.txt | awk '{print $1}' )
        #將temp.txt的總行數列出並設為變數X，要用awk是因為wc -l也會把檔名列出來，因此只需要印出第一個位置的資料(即 總行數)
        Y=1
        while test $X == 0
        do
            echo
            echo '===================================================='
            echo
            echo '資料夾中沒有找到.log檔，請重新上傳.log檔到資料夾中'
            echo
            echo '===================================================='
            echo
            echo
            break
        done

        while test $Y -le $X
        #當變數Y小於X的情況下，就執行以下的do loop
        do
            #將temp.txt檔中的第B行資料抓出來設為變數name
            name=$(sed -n "${Y}p" temp.txt|sed 's/.log//g')
            
            #抓出特定檔中含Standard orientation的行號，並print最後一個行號設為變數A
            A=$(grep -n -o 'Standard orientation' $name.log|cut -d: -f1|tail -1)

            #抓出特定檔中含NAtoms的行號，並設為變數nAtoms
            nAtoms=$(grep -n 'NAtoms' $name.log|cut -d: -f1|tail -1)
            
            #抓出行號nAtoms那一樣的資料，並抓出排序在第二個位置的單字設為變數NAtoms(因為需要知道這個結構共幾個原子組成)
            NAtoms=$(sed -n "${nAtoms}p" $name.log|awk '{print $2}')

            #設B為變數A+1000後的數值
            B=$(expr "$A" + 1000)
            
            #設C為變數NAtoms+1後的數值
            C=$(expr "$NAtoms" + 1)
            
            #設變數coordination為變數A(含)以下1000行的內容，並砍掉不要的資訊(從第C行到1000行)，最後印出結果的第四、五、六個位置的資料(座標)
            coordination=$(sed -n "${A},${B}p" $name.log|sed '1,5d'|sed "${C},1000d"|awk '{print $4,$5,$6}')
            #expr "$A" + 1000是將變數A從字串轉為數字後加上1000
            #如果要進行sed -n的行數是變量，那就要按上面的寫法才能正確抓取內容

            #將變數coordination(截出來的座標)另存成$name-coordination.txt檔
            cat << END > $name-coordination.txt
$coordination
END
            
            #用上述一樣的方法取得atom的名稱並存成$name-atom.txt檔(只是這次抓的是Distance matrix)
            #如果系統的原子數量太少，log檔裡不會有Distance matrix可抓，這時候就會有bug(像氫分子的log檔內就沒有Distance matrix可以抓)。
            if grep -q "Distance matrix" $name.log; then 
                A2=$(grep -n -o 'Distance matrix' $name.log|cut -d: -f1|tail -1)
                nAtoms=$(grep -n 'NAtoms' $name.log|cut -d: -f1|tail -1)
                NAtoms=$(sed -n "${nAtoms}p" $name.log|awk '{print $2}')
                B2=$(expr "$A2" + 1000)
                C2=$(expr "$NAtoms" + 1)
                atom=$(sed -n "${A2},${B2}p" $name.log|sed '1,2d'|sed "${C2},1000d"|awk '{print $2}')
                cat << END > $name-atom.txt
$atom
END

                #用paste將兩個.txt結合在一起並產生一個新的$name_atom_list.txt檔，並將txt檔中的所有內容設為變數coordination。
                paste $name-atom.txt $name-coordination.txt > $name-atom_list.txt
                coordination=$(cat $name-atom_list.txt)

                rm $name-atom.txt
                rm $name-coordination.txt
                

                #經過part1的篩選後，同個路徑底下的setting檔，理論上只會剩default setting、user setting當中的其中一種。
                #不過為了以防萬一出了啥特殊bug，所以用elif撰寫，不使用else。
                if [ -f default_setting_temp ]; then
                    setting=$(grep -A 6 '%nprocshared' default_setting_temp)
                elif [ -f user_setting_temp ]; then
                    setting=$(grep -A 6 '%nprocshared' user_setting_temp)
                fi

                cat << END > $name.com
%chk=$name.chk
$setting

$charge $multiplicity
$coordination

END
                echo
                dos2unix $name.com #這行是用來處理掉系統造成的換行符號
                
                #vi $name.com #如果有需要改.com檔的內容，就把這行加上去，改完存完檔就能自動上傳了
                #~/mksh $name #如果需要直接將com檔拿去送，就補這行

                if grep -q "Title Card Required" $name.com; then
                    echo -e "<> \e[1;32;40m$name.com\e[0m has done! "
                else
                    echo -e "<> \033[31m$name.com\033[0m doesn't have coordination!!!!!!! "
                fi

                rm $name.log #如果需要刪掉原本上傳的log檔就補這行
                rm $name-atom_list.txt
                Y=$(expr $Y + 1)
                #執行完上述所有命令後將變數Y+1，這樣才能讓迴圈繼續下去。
            else
                rm $name-coordination.txt
                echo
                echo  -e "<> \033[31m$name.log\033[0m 檔內就沒有Distance matrix可以抓，需另存成gjf進行轉檔"
                Y=$(expr $Y + 1)
            fi
        done
        rm temp.txt
        echo
        echo
        read -p "按任意鍵繼續..."
        ;;

    3)
        echo
        while :
        do
        clear
        echo
        echo '3a) default setting'
        echo
        echo '3b) user setting'
        echo
        echo 'b) back to last page'
        echo
        echo 'x) exit'
        echo
        echo -n 'which one? '
        read function3
        echo

        case "$function3" in
            3a)
                #先把目前路徑底下的setting檔都清空
                #如果default_setting_temp存在，那就刪掉default_setting_temp。
                if [ -f "default_setting_temp" ]; then
                    rm default_setting_temp
                fi

                #如果user_setting_temp存在，那就刪掉user_setting_temp。
                if [ -f "user_setting_temp" ]; then
                    rm user_setting_temp
                fi

                #再重新建一個default_setting_temp
                cat << END > default_setting_temp
%nprocshared=4
%mem=512MW
# b3lyp/cc-pVTZ opt freq

Title Card Required
END

                #提醒一下使用者目前的設定為default設定
                clear
                echo '================================='
                echo '【currrent setting(default setting)】'
                echo '  CPU：4'
                echo '  memory：512MW'
                echo '  hybrid functional：b3lyp'
                echo '  basis set：cc-pVTZ'
                echo '================================='
                #預設為4CPU、512MW的記憶體，計算用的hybrid functional是b3lyp，basis set是cc-pVTZ。
                echo
                echo
                read -p "按任意鍵繼續..."
                ;;

            3b)
                #先把目前路徑底下的setting檔都清空
                #如果default_setting_temp存在，那就刪掉default_setting_temp。
                if [ -f "default_setting_temp" ]; then
                    rm default_setting_temp
                fi

                #如果user_setting_temp存在，那就刪掉user_setting_temp。
                if [ -f "user_setting_temp" ]; then
                    rm user_setting_temp
                fi

                #讓使用者輸入參數
                read -p 'How many CPU of this job? (4/8/16/32/64)=>' CPU
                echo
                echo '1MW=8MB 1GB=1024MB=128MW'                
                read -p 'What is the unit of memory? (MB/MW/GB)=>' memory_unit
                echo
                read -p 'How much memory of this job? (64/128/256/512/1024)=>' memory
                echo
                read -p 'Which hybrid functional? (b3lyp/mp2/HF)=>' hybrid_functional
                echo
                read -p 'Which basis set? (cc-pVTZ/cc-pVDZ/cc-pVQZ)=>' basis_set                

                #建一個user_setting_temp
                cat << END > user_setting_temp
%nprocshared=$CPU
%mem=$memory$memory_unit
# $hybrid_functional/$basis_set opt freq

Title Card Required
END

                #提醒一下使用者目前的設定為user設定
                clear
                echo '================================='
                echo '【currrent setting(user setting)】'
                echo '  CPU：'$CPU
                echo '  memory：'$memory$memory_unit
                echo '  hybrid functional：'$hybrid_functional
                echo '  basis set:' $basis_set
                echo '================================='
                echo
                echo
                read -p "按任意鍵繼續..."
                ;;
            b)
                break
                ;;

            x)
                exit
                ;;

            *)
                echo
                echo 'wrong, none of the above. do try again.'
                sleep 2
                ;;
            esac
        done
      ;;

    4)
        #創建一個叫temp.txt的檔
        cat << END > input.txt
更名前 更名後

END

        #vi input.txt的檔，讓使用者輸入資料
        vi input.txt

        #截取vi temp.txt更名前 更名後那行以下1000行的資料，且不包更名前 更名後那行，並將這些資料設為變數
        will_change_job=$(grep -A 1000 '更名前 更名後' input.txt|sed '1,1d')

        cat << END > temp.txt
$will_change_job
END

        read -p "Which type of name need to change? (ex：gjf/com/chk/log/out/txt) " Type

        X=$(wc -l temp.txt | awk '{print $1}' )
        #將temp.txt的總行數列出並設為變數X，要用awk是因為wc -l也會把檔名列出來，因此只需要印出第一個位置的資料(即 總行數)
        Y=1
                #當變數Y小於X的情況下，就執行以下的do loop
                while test $Y -le $X
                do

                #將temp.txt檔中的第Y行，第一個資料資料抓出來設為變數name，並把檔名中的.log裁掉
                name=$(sed -n "${Y}p" temp.txt|awk '{print $1}'|sed 's/.log//g')

                #將temp.txt檔中的第Y行，第二個資料抓出來設為變數NAME
                NAME=$(sed -n "${Y}p" temp.txt|awk '{print $2}')

                    #這段就輸入要把name變數代入什麼功能        
                    mv $name.$Type $NAME.$Type
                    echo -e "<> \e[1;32;40m$NAME.$Type\e[0m is OK! "

                    #執行完上述命令後將變數Y+1
                    Y=$(expr $Y + 1 )
                done
                rm temp.txt
                rm input.txt
        read -p "按任意鍵繼續..."
        ;;
    5)
        #創建一個叫temp.txt的檔
        cat << END > input.txt
job

END

        #vi input.txt的檔，讓使用者輸入資料
        vi input.txt

        #截取vi temp.txt job那行以下1000行的資料，且不包job那行，並將這些資料設為變數
        will_sub_job=$(grep -A 1000 'job' input.txt|sed '1,1d')

        cat << END > temp.txt
$will_sub_job
END

        #將temp.txt的總行數列出並設為變數X，要用awk是因為wc -l也會把檔名列出來，因此只需要印出第一個位置的資料(即 總行數)
        X=$(wc -l temp.txt | awk '{print $1}' )
        Y=1
            #當變數Y小於X的情況下，就執行以下的do loop
            while test $Y -le $X
            do

            #將temp.txt檔中的第Y行，第一個資料資料抓出來設為變數name，並把檔名中的.log裁掉
            name=$(sed -n "${Y}p" temp.txt|awk '{print $1}'|sed 's/.log//g')

                #這段就輸入要把name變數代入什麼功能
                ~/mksh $name

                #執行完上述命令後將變數Y+1
                Y=$(expr $Y + 1 )
            done
            rm temp.txt
            rm input.txt
        read -p "按任意鍵繼續..."
        ;;
    x)
      break
      ;;
    *)
      echo
      echo 'wrong, none of the above. do try again.'
      sleep 2
      ;;
  esac
done
