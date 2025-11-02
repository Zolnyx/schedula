import threading

class GPUCluster:
    def __init__(self, total_gpus=4, total_mem=32):
        self.total_gpus = total_gpus
        self.total_mem = total_mem
        self.available_gpus = total_gpus
        self.available_mem = total_mem
        self.lock = threading.Lock()

    def allocate_resources(self, gpu_req, mem_req):
        with self.lock:
            if gpu_req <= self.available_gpus and mem_req <= self.available_mem:
                self.available_gpus -= gpu_req
                self.available_mem -= mem_req
                return True
            return False

    def release_resources(self, gpu_req, mem_req):
        with self.lock:
            self.available_gpus += gpu_req
            self.available_mem += mem_req
