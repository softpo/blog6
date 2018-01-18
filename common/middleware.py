# coding: utf-8

import time

from django.utils.deprecation import MiddlewareMixin

MAX_REQUEST_PER_SECOND = 20  # 每秒最大请求次数

# 可保存的位置
# ------------
#   缓存 -> session
#   DB     (耗时长)
#   文件    (无法分布式运算)
#   全局变量 (无法分布式运算)

# 保存数据类型: list


class RequestBlockingMiddleware(MiddlewareMixin):
    '''限制用户的访问频率最大为每秒 5 次, 超过 2 次时, 等待至合理时间再返回'''
    def process_request(self, request):
        # 获得当前时间戳
        now = time.time()
        # 取出历史时间队列
        request_queue = request.session.get('request_queue', [])
        # 判断队列长度
        if len(request_queue) < MAX_REQUEST_PER_SECOND:
            # 小于额定队列, 放行
            request_queue.append(now)
            request.session['request_queue'] = request_queue
            print('放行')
        else:
            # 达到额定队列长度, 检查与最早时间戳的时差
            time0 = request_queue[0]
            if (now - time0) < 1:
                print('waitting---------------------', int(now))
                time.sleep(10)  # 请求太频繁, 等待 10 秒
                print('return-----------------------', int(time.time()))

            request_queue.append(time.time())
            request.session['request_queue'] = request_queue[1:]  # 截取列表, 维持额定队列长度, 让时间队列滚动更新
