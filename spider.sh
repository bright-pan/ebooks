#!/usr/bin/env bash

DISPLAY=:0

test -f venv/bin/activate && \
    source venv/bin/activate

function show_help(){
    echo "$0"
    echo
    echo "List Projects names"
    echo "  $0 list"
    echo
    echo "List Spiders names"
    echo "  $0 <project-name> list"
    echo
    echo "Start Crawling with spider"
    echo "$0 <project-name> <spider-name>"
    echo
    echo "Show Spider PID"
    echo "$0 pid <spider-name>"
    echo
    echo "Run Spider Parse function"
    echo "$0 <project-name> parse <spider-name> <function-name> <url>"
}
function spider_pid() {
    SPIDER=$1
    if [ "$SPIDER" != "" ]; then
        ps aux|grep -i "$SPIDER"|grep -v "grep"|grep -v "$0"|head -n1|awk '{print $2}'
    fi
}

if [ "$1" == "" ]; then
    show_help
elif [ "$1" == "list" ]; then
    ls crawlers/|grep -v __init__|xargs -0
elif [ "$1" == "pid" ]; then
    spider_pid $2
else
    PROJECT_NAME=$1
    test -d "crawlers/$PROJECT_NAME/$PROJECT_NAME" && \
        cd "crawlers/$PROJECT_NAME/$PROJECT_NAME"
    if [ "$2" == "list" ]; then
        #list spiders in project
        scrapy list
    elif [ "$2" == "parse" ]; then
        if [ "$3" != "" ]; then
            if [ "$4" != "" ]; then
                if [ "$5" != "" ]; then
                    test -f ./proxychains.conf && \
                        proxychains4 scrapy parse --spider="$3" -c "$4" -d 100 -v "$5"
                else
                    show_help
                fi
            else
                show_help
            fi
        else
            show_help
        fi
    else
        # start spider
        test -f ./proxychains.conf && proxychains4 scrapy crawl $2
    fi
fi