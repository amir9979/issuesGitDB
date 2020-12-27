import json

from diff import get_changed_methods

if __name__ == "__main__":
    commits = ['00dc479f6a1d204d557f4cb1d981ba236fe09565', '00fee20efcd5d1e79cfcac501f19f2163a34fd09',
               '0343b4fda87161265acf30d5ee61e525e751358d', '05763470e5a067eb153533d47baa73174ad9bd46',
               '0820c4c895f6e7c9ef4860d7373675550c87ac6c', '0d0061f247b9c28b59b1af7e7a10def74718ac94',
               '159415855d06d186e86a70f3d4aba8c2e96d4b34', '15e1ea2f4e5affe377fc303c1f637a73e3fbe625',
               '2aae22de23bf47566700c0ca2671d25e30c4a857', '2d9a9ae59fd3b753e05903f63641eff1203f1bd1',
               '2dfca4a424fe60e2bbb99cf5e0a5f9352142cc08', '2fb9e71da695f4ffc1d390209944399b12c53a5d',
               '30c85ad05363767deeefee577063c2c432b971d4', '358f139d1316df2b8efd7610afa3aa68d165334f',
               '362dd935f84ef80b13cced13a74339e42c775809', '38bafd283f2e5fed8ca33dcf1aac8e4bdf54450e',
               '38f8b88528487efc4e53ac6c91f08fbaaa2a82d6', '3a4ac357981283fd3a8817f9e6d57e8b181549be',
               '3a8595f1a57759044be301fc76a2300b7f2efe66', '408462e80d57be420c153b67f69110e27776d4eb',
               '43a9bab8c010d66744ae02b2d26020a946235202', '43cf3f491e7b9b42dc4a5fa4d7bc00cef1d38f7e',
               '4fc5c6b35c1ca02fb0e876d54342c66196aac846', '506bd018b3ca638cd0c9d1bdad627f6468a05bee',
               '529964961fd1575013297bc6d4db4528133ee371', '59311cc13a0bc99cacf03e00da93423b20b3d459',
               '5a509030a946646780e963b9f492a4eaff734116', '5acf310d08b2bc5182cf936616ef70938cb2c499',
               '5c3ec55e15922c58bb2f39145de9fe641840bb50', '5e62bf80f345ff28d494c2b407a9e8691a9fb684',
               '6049e77fdcd021544a60651fc6de4d80e2ef1c2d', '61836183b1d84a18dbcc084d1f41bcecf752f9fd',
               '65b5dc69db3bfd08b4392dcee16fa0542b097812', '66a37174a0398d76ff95904c22e77bc65890eec0',
               '68acbc803e416a38616bc25505cb88dde81af5ca', '708da45999d8e545bfbae17a092c68df94061756',
               '79f7a7ef529ae656a80f7e331f75e79999cef7ea', '7d3fbbfd43ec66fab190b29db9f7e157791de37f',
               '7fd021d82ff431fb31f42bc6c5c44a3b979cb426', '8252b04a45722648ce2225853de9882b3b0de034',
               '8a8859cb88a49a8b967217bfc1daafe0805e7c86', '8d360ae70732ae26d961f76da5a98c44ac5931c6',
               '8e8e78d849825696237b9f540f3e082a44b1e838', '91ac16e0b4a74b437d86c2dd7a47272105b4317c',
               '97f1c120c092916f2f95439b6440a8977c66ee0a', 'a01e450694ee3d6049dd637ae700f36d173d6463',
               'a9a73a7b2df1455646a7e0207712be6d4412e817', 'bb8709f3e30e7c13530dfef458a4c370783de2be',
               'bea1ae92aa52a985f8c171c6e17ff7fc4aa61fe4', 'c0041cafc2fda3fb437009d5417ba5ebeb32ad35',
               'c3b1fefbad0c67c8556ba6b4573f135197f87598', 'cc1aed9bdf196403c673a886bbf723101171a9bf',
               'cc991feadbcee678635f7831ad8091ab8698d508', 'd6ad3f01574b839670d4ea5cf82a601eee7e0c16',
               'd99f581745097c9562f1d701a6da66cd81a550f2', 'dd5a0e6e1e3edb41afb4b40e4ec2c99e5932e73c',
               'ddc06197e4c9cdd009ba2a039dca77099797c584', 'e7d16c27629722a93a9d36a0b5e0a3a793850544',
               'ed14537b802be2bce96c8d5a0e056daeb6f11b0c', 'ed7e9b43494e490a51c25c410b2950005fd685ea',
               'f13d18cff3f0932e727dda04bf80008fc2fbbc70', 'f30c4607a2b6dcc7dc4476d321fc1de32ce9b780',
               'f5a9effebd7209f3fa5385f18a5e59e8a09122f2', 'f7a005e41b55215aa91c0fd244878f0fad11ec53']
    json_out_file = r"c:\temp\rotem_bugs.json"
    buggy = dict()
    for commit in commits:
        methods = filter(lambda x: 'test' not in x.lower(), get_changed_methods(r"C:\Temp\commons-lang", commit))
        if methods:
            buggy[commit] = methods
    with open(json_out_file, "wb") as f:
        json.dump(buggy, f)
    pass
