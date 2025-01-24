from redis.sentinel import Sentinel
import time
import sys


def test_redis_sentinel():
    try:
        print("正在连接 Sentinel...")
        sentinel = Sentinel([
            ('101.32.116.114', 31332)  # 使用实际的 LoadBalancer IP 和端口
        ],
            socket_timeout=1.0
        )

        # 1. 测试主节点信息
        print("\n1. 测试获取主从节点信息:")
        master_info = sentinel.discover_master('mymaster')
        slave_info = sentinel.discover_slaves('mymaster')
        print(f"主节点信息: {master_info}")
        print(f"从节点信息: {slave_info}")

        # 2. 测试读写操作
        print("\n2. 测试读写操作:")
        master = sentinel.master_for('mymaster', password='dap!1Seata', socket_timeout=1.0)
        slave = sentinel.slave_for('mymaster', password='dap!1Seata', socket_timeout=1.0)

        # 写入测试
        print("写入数据...")
        master.set('test_key', 'test_value')

        # 读取测试
        print("从主节点读取:", master.get('test_key'))
        print("从从节点读取:", slave.get('test_key'))

        # 3. 测试批量操作
        print("\n3. 测试批量操作:")
        pipe = master.pipeline()
        for i in range(5):
            pipe.set(f'key_{i}', f'value_{i}')
        pipe.execute()
        print("批量写入完成")

        # 读取批量写入的数据
        for i in range(5):
            value = slave.get(f'key_{i}')
            print(f"key_{i} = {value}")

        # 4. 清理测试数据
        print("\n4. 清理测试数据:")
        master.delete('test_key')
        for i in range(5):
            master.delete(f'key_{i}')
        print("测试数据已清理")

    except Exception as e:
        print(f"错误类型: {type(e)}", file=sys.stderr)
        print(f"错误信息: {str(e)}", file=sys.stderr)
        print("堆栈跟踪:", file=sys.stderr)
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_redis_sentinel()