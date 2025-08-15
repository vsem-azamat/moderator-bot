"""Performance tests for repository operations."""

import asyncio
import time

import pytest
from app.domain.repositories import IChatRepository, IUserRepository

from tests.factories import ChatFactory, UserFactory


@pytest.mark.performance
@pytest.mark.slow
class TestRepositoryPerformance:
    """Performance tests for repository operations."""

    async def test_bulk_user_creation_performance(self, user_repository: IUserRepository):
        """Test performance of bulk user creation."""
        # Test with different batch sizes
        batch_sizes = [10, 50, 100, 500]

        for batch_size in batch_sizes:
            users = UserFactory.create_batch(batch_size)

            start_time = time.time()

            # Save users one by one (sequential)
            for user in users:
                await user_repository.save(user)

            sequential_time = time.time() - start_time

            # Save users concurrently
            new_users = UserFactory.create_batch(batch_size)
            start_time = time.time()

            save_tasks = [user_repository.save(user) for user in new_users]
            await asyncio.gather(*save_tasks)

            concurrent_time = time.time() - start_time

            print(f"Batch size {batch_size}:")
            print(f"  Sequential: {sequential_time:.3f}s ({sequential_time / batch_size:.3f}s per user)")
            print(f"  Concurrent: {concurrent_time:.3f}s ({concurrent_time / batch_size:.3f}s per user)")
            print(f"  Speedup: {sequential_time / concurrent_time:.2f}x")

            # Concurrent should be faster for larger batches
            if batch_size >= 50:
                assert concurrent_time < sequential_time

    async def test_bulk_user_retrieval_performance(self, user_repository: IUserRepository):
        """Test performance of bulk user retrieval."""
        # Create test data
        batch_size = 1000
        users = UserFactory.create_batch(batch_size)

        # Save all users first
        save_tasks = [user_repository.save(user) for user in users]
        await asyncio.gather(*save_tasks)

        user_ids = [user.id for user in users]

        # Test sequential retrieval
        start_time = time.time()

        retrieved_users_sequential = []
        for user_id in user_ids:
            user = await user_repository.get_by_id(user_id)
            if user:
                retrieved_users_sequential.append(user)

        sequential_time = time.time() - start_time

        # Test concurrent retrieval
        start_time = time.time()

        retrieve_tasks = [user_repository.get_by_id(user_id) for user_id in user_ids]
        retrieved_users_concurrent = await asyncio.gather(*retrieve_tasks)
        retrieved_users_concurrent = [user for user in retrieved_users_concurrent if user]

        concurrent_time = time.time() - start_time

        print(f"Retrieval of {batch_size} users:")
        print(f"  Sequential: {sequential_time:.3f}s")
        print(f"  Concurrent: {concurrent_time:.3f}s")
        print(f"  Speedup: {sequential_time / concurrent_time:.2f}x")

        # Verify we got all users
        assert len(retrieved_users_sequential) == batch_size
        assert len(retrieved_users_concurrent) == batch_size

        # Concurrent should be significantly faster
        assert concurrent_time < sequential_time

    async def test_blocked_users_query_performance(self, user_repository: IUserRepository):
        """Test performance of blocked users query with large dataset."""
        # Create mix of blocked and normal users
        total_users = 10000
        blocked_percentage = 0.1  # 10% blocked
        blocked_count = int(total_users * blocked_percentage)

        print(f"Creating {total_users} users ({blocked_count} blocked)")

        # Create users
        normal_users = UserFactory.create_batch(total_users - blocked_count, is_blocked=False)
        blocked_users = UserFactory.create_batch(blocked_count, is_blocked=True)
        all_users = normal_users + blocked_users

        # Save all users concurrently
        start_time = time.time()
        save_tasks = [user_repository.save(user) for user in all_users]
        await asyncio.gather(*save_tasks)
        creation_time = time.time() - start_time

        print(f"User creation took: {creation_time:.3f}s")

        # Test blocked users query performance
        start_time = time.time()

        retrieved_blocked_users = await user_repository.get_blocked_users()

        query_time = time.time() - start_time

        print(f"Blocked users query took: {query_time:.3f}s")
        print(f"Found {len(retrieved_blocked_users)} blocked users")

        # Verify results
        assert len(retrieved_blocked_users) == blocked_count
        assert all(user.is_blocked for user in retrieved_blocked_users)

        # Query should be reasonably fast (under 1 second for 10k users)
        assert query_time < 1.0

    async def test_chat_operations_performance(self, chat_repository: IChatRepository):
        """Test performance of chat operations."""
        batch_size = 1000
        chats = ChatFactory.create_batch(batch_size)

        # Test bulk creation
        start_time = time.time()
        save_tasks = [chat_repository.save(chat) for chat in chats]
        await asyncio.gather(*save_tasks)
        creation_time = time.time() - start_time

        print(f"Created {batch_size} chats in {creation_time:.3f}s")
        print(f"Average: {creation_time / batch_size:.3f}s per chat")

        # Test get_all performance
        start_time = time.time()
        all_chats = await chat_repository.get_all()
        query_time = time.time() - start_time

        print(f"Retrieved {len(all_chats)} chats in {query_time:.3f}s")

        assert len(all_chats) == batch_size

        # Both operations should be reasonably fast
        assert creation_time < 5.0  # 5 seconds for 1000 chats
        assert query_time < 1.0  # 1 second to retrieve all

    async def test_concurrent_mixed_operations_performance(self, user_repository: IUserRepository):
        """Test performance of mixed concurrent operations."""
        # Simulate real-world mixed workload
        num_operations = 1000

        async def random_user_operation(index: int):
            """Perform a random user operation."""
            import random

            user_id = 500000000 + index
            operation = random.choice(["create", "read", "update", "block", "unblock"])

            if operation == "create":
                user = UserFactory.create(id=user_id)
                return await user_repository.save(user)

            if operation == "read":
                return await user_repository.get_by_id(user_id)

            if operation == "update":
                # Try to get user first, create if doesn't exist
                user = await user_repository.get_by_id(user_id)
                if not user:
                    user = UserFactory.create(id=user_id)
                else:
                    user.username = f"updated_{index}"
                return await user_repository.save(user)

            if operation == "block":
                user = await user_repository.get_by_id(user_id)
                if not user:
                    user = UserFactory.create(id=user_id, is_blocked=True)
                else:
                    user.block()
                return await user_repository.save(user)

            if operation == "unblock":
                user = await user_repository.get_by_id(user_id)
                if user and user.is_blocked:
                    user.unblock()
                    return await user_repository.save(user)
                return user
            return None

        # Execute mixed operations concurrently
        start_time = time.time()

        operation_tasks = [random_user_operation(i) for i in range(num_operations)]
        results = await asyncio.gather(*operation_tasks, return_exceptions=True)

        total_time = time.time() - start_time

        # Count successful operations
        successful_ops = sum(1 for result in results if not isinstance(result, Exception))
        failed_ops = len(results) - successful_ops

        print("Mixed operations performance:")
        print(f"  Total operations: {num_operations}")
        print(f"  Successful: {successful_ops}")
        print(f"  Failed: {failed_ops}")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Average time per operation: {total_time / num_operations:.3f}s")
        print(f"  Operations per second: {num_operations / total_time:.1f}")

        # Most operations should succeed
        assert failed_ops < num_operations * 0.1  # Less than 10% failures

        # Should achieve reasonable throughput
        ops_per_second = num_operations / total_time
        assert ops_per_second > 100  # At least 100 ops/sec


@pytest.mark.performance
@pytest.mark.slow
class TestMemoryUsagePerformance:
    """Test memory usage and efficiency."""

    async def test_large_dataset_memory_usage(self, user_repository: IUserRepository):
        """Test memory usage with large datasets."""
        import os

        import psutil

        process = psutil.Process(os.getpid())

        # Measure initial memory
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create large dataset
        batch_size = 10000
        users = UserFactory.create_batch(batch_size)

        # Memory after creating objects
        after_creation_memory = process.memory_info().rss / 1024 / 1024

        # Save to database
        save_tasks = [user_repository.save(user) for user in users]
        await asyncio.gather(*save_tasks)

        # Memory after database operations
        after_db_memory = process.memory_info().rss / 1024 / 1024

        # Clear references
        del users
        del save_tasks

        # Force garbage collection
        import gc

        gc.collect()

        # Memory after cleanup
        after_cleanup_memory = process.memory_info().rss / 1024 / 1024

        print(f"Memory usage test with {batch_size} users:")
        print(f"  Initial: {initial_memory:.1f} MB")
        print(f"  After creation: {after_creation_memory:.1f} MB (+{after_creation_memory - initial_memory:.1f} MB)")
        print(f"  After DB ops: {after_db_memory:.1f} MB (+{after_db_memory - initial_memory:.1f} MB)")
        print(f"  After cleanup: {after_cleanup_memory:.1f} MB (+{after_cleanup_memory - initial_memory:.1f} MB)")

        # Memory should not grow excessively
        total_growth = after_cleanup_memory - initial_memory
        assert total_growth < 100  # Should not use more than 100MB for this test
